#!/usr/bin/env python3
"""Paper-trading tracker: run the Hyperliquid copy engine against LIVE
mainnet data on a schedule (cron every 30 min).

Each run is incremental, idempotent and crash-safe:
  * per-target watermarks + fill-hash dedup -> a fill is never
    processed twice, even if a run is re-executed;
  * state is written atomically (tmp file + rename);
  * one bad target never kills the run;
  * missing/corrupt state -> start fresh with a warning.

What a run does, per target (vault or wallet address):
  1. Re-score the target at most every 6h from its trailing-30d fills
     (exact engine logic: scorer.score_wallet / classify — FIFO
     realized PnL, time-weighted win rate / profit factor, consistency,
     drawdown, minimum-sample guard). Copy only if score >= 65 AND
     >= 10 closed trades.
  2. Fetch fills since the watermark (chunked time windows), dedup by
     fill hash, skip Settlement fills.
  3. Opens: aggregate fragmented fills into one intent per
     (coin, direction) within 120s, then run the copy decision:
     classification must be "copy"; size = 2% of the $10k paper
     account, shrunk by the fractional-Kelly cap from the target's
     measured edge (sizing.kelly_fstar — skipped entirely when edge
     <= 0); one paper position per (target, coin).
  4. Closes: close the matching paper position PROPORTIONALLY
     (closePct = fill.sz / |target startPosition|) at the target's
     fill price.
  5. Independent exits on every open position against live mids:
     stop-loss 8%, take-profit 20%, trailing 2%, max hold 24h
     (exits.py logic, with the trailing peak persisted in state so it
     survives restarts).
  6. Fees: taker 0.035% + slippage 0.02% per side on every paper fill.

Outputs:
  paper_trades.csv   - every paper fill (append-only)
  paper_summary.json - rebuilt from the CSV each run (self-healing)
  paper_state.json   - watermarks, seen hashes, open positions
  paper_tracker.log  - run log

Stdlib only. No websocket-client: polling survives restarts.
"""
from __future__ import annotations

import csv
import json
import os
import sys
import time
import traceback
import urllib.error
import urllib.request
from datetime import datetime, timezone

# --------------------------------------------------------------------------
# Engine logic reuse (exact: FIFO scorer, Kelly sizing)
# --------------------------------------------------------------------------
ENGINE_DIR = os.path.expanduser("~/workspace/copytrade-robinhood/hyperliquid")
sys.path.insert(0, ENGINE_DIR)
try:
    from scorer import score_wallet, classify, realized_closes
    from sizing import kelly_fstar
except ImportError as e:  # fail fast at startup, never silently wrong
    print(f"FATAL: cannot import engine modules from {ENGINE_DIR}: {e}",
          file=sys.stderr)
    sys.exit(1)

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------
BASE_DIR = os.path.expanduser("~/workspace/copy-trading")
TARGETS_PATH = os.path.join(BASE_DIR, "paper_targets.json")
STATE_PATH = os.path.join(BASE_DIR, "paper_state.json")
CSV_PATH = os.path.join(BASE_DIR, "paper_trades.csv")
SUMMARY_PATH = os.path.join(BASE_DIR, "paper_summary.json")
LOG_PATH = os.path.join(BASE_DIR, "paper_tracker.log")

INFO_URL = "https://api.hyperliquid.xyz/info"
HTTP_TIMEOUT = 30

EQUITY_USD = 10000.0
RISK_PCT = 0.02            # -> $200 max risk per paper position
KELLY_FRACTION = 0.25      # quarter-Kelly, as in sizing.py
KELLY_MIN_CLOSES = 10
MIN_NOTIONAL_USD = 10.0    # skip dust-sized copies

FEE_RATE = 0.00035          # taker fee per side
SLIPPAGE = 0.00020          # slippage assumption per side
FEE_SIDE = FEE_RATE + SLIPPAGE  # 0.055% charged on every paper fill

MIRROR_SCORE = 65.0
FADE_SCORE = 30.0
MIN_CLOSED = 10             # minimum-sample guard: never copy below this
SCORE_TTL_S = 6 * 3600      # re-score at most every 6h
SCORE_LOOKBACK_DAYS = 30
STALE_CUTOFF_S = 6 * 3600   # fills older than this are marked seen, not copied
INTENT_WINDOW_S = 120.0     # fragment clustering window
MAX_LOOKBACK_S = 7 * 86400  # never fetch more than 7d incrementally

STOP_LOSS_PCT = 8.0
TAKE_PROFIT_PCT = 6.0    # was 20.0 (never fired in 3,716 backtest legs); 6% banks
                         # runners before the tight trail gets wicked out
TRAILING_PCT = 1.0         # was 2.0; 1% is the robust grid-search winner
MAX_HOLD_S = 24 * 3600
# Coins proven dead weight in the 30d backtest (flat-to-negative copy edge).
# Everything else (including new coins from new vaults) is allowed.
COIN_BLOCKLIST = {"BTC", "ETH", "BNB", "LINK", "DOGE"}
# Walk-forward guard: pause a target whose own paper book decays.
WF_PAUSE_MIN_TRADES = 10   # need at least this many closed paper trades
WF_PAUSE_WINDOW = 20       # trailing window evaluated

MAX_FILLS_PER_CHUNK = 1990  # userFillsByTime cap is ~2000
MAX_CHUNKS = 64
SEEN_CAP = 8000

SCORER_WEIGHTS = {"win_rate": 25, "profit_factor": 20, "consistency": 15,
                  "max_drawdown": 15, "sample_size": 15, "recency": 10}

CSV_FIELDS = ["ts", "target", "coin", "side", "action", "size", "price",
              "fee_usd", "realized_pnl_usd", "paper_equity_usd", "reason",
              "fill_hash"]

CSV_PREAMBLE = [
    "# paper_tracker.py — Hyperliquid copy-engine paper test (live mainnet fills)",
    "# ASSUMPTIONS: paper fills assume a full fill at the target's fill price;",
    "#   no market impact; no funding payments modeled; exits evaluated on",
    "#   30-min cadence against public mids.",
    "# COSTS: taker fee 0.035% + slippage 0.02% per side (0.055%/side,",
    "#   0.11% round-trip), charged on every paper fill.",
    "# realized_pnl_usd on closes is NET of both sides' fees.",
]


# --------------------------------------------------------------------------
# Logging / state
# --------------------------------------------------------------------------
def log(msg: str) -> None:
    line = f"{datetime.now(timezone.utc):%Y-%m-%dT%H:%M:%SZ} {msg}"
    print(line, flush=True)
    try:
        with open(LOG_PATH, "a") as f:
            f.write(line + "\n")
    except OSError:
        pass


def fresh_state() -> dict:
    return {"targets": {}, "positions": [], "next_id": 1,
            "realized_pnl_usd": 0.0, "fees_paid_usd": 0.0, "run_count": 0}


def load_state() -> dict:
    try:
        with open(STATE_PATH) as f:
            st = json.load(f)
        st.setdefault("targets", {})
        st.setdefault("positions", [])
        st.setdefault("next_id", 1)
        st.setdefault("realized_pnl_usd", 0.0)
        st.setdefault("fees_paid_usd", 0.0)
        st.setdefault("run_count", 0)
        return st
    except (OSError, json.JSONDecodeError, ValueError) as e:
        log(f"WARN state unreadable ({e}); starting fresh")
        return fresh_state()


def save_state(state: dict) -> None:
    tmp = STATE_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f)
    os.replace(tmp, STATE_PATH)  # atomic


def load_targets() -> list[dict]:
    """Lenient loader: placeholders and bad entries are skipped with a
    warning, never fatal (one bad target must not kill a cron run)."""
    try:
        with open(TARGETS_PATH) as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        log(f"WARN targets unreadable ({e}); no targets this run")
        return []
    out = []
    for w in data.get("wallets", []):
        addr = str(w.get("address", ""))
        label = str(w.get("label", addr))
        if "REPLACE_ME" in addr.upper():
            continue  # placeholder, filled in later
        if not (addr.startswith("0x") and len(addr) == 42):
            log(f"WARN skipping malformed target address {addr!r}")
            continue
        kind = str(w.get("kind", "wallet")).lower()
        if kind not in ("wallet", "vault"):
            log(f"WARN skipping {addr}: bad kind {kind!r}")
            continue
        out.append({"address": addr.lower(), "label": label, "kind": kind})
    return out


# --------------------------------------------------------------------------
# Hyperliquid public API (polling client)
# --------------------------------------------------------------------------
def api_post(payload: dict):
    """POST to /info with 30s timeout, one retry on transient failures."""
    data = json.dumps(payload).encode()
    last: Exception | None = None
    for attempt in (1, 2):
        try:
            req = urllib.request.Request(
                INFO_URL, data=data,
                headers={"Content-Type": "application/json",
                         "User-Agent": "paper-tracker/0.1"})
            with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt == 1:
                time.sleep(3)
                continue
            raise
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            last = e
            if attempt == 1:
                time.sleep(3)
                continue
            raise
    raise RuntimeError(f"unreachable: {last}")


def fetch_fills_window(address: str, start_ms: int, end_ms: int) -> list[dict]:
    """Fetch fills in [start_ms, end_ms], splitting the window when a
    chunk hits the ~2000-fill cap."""
    chunks = [(start_ms, end_ms)]
    out: list[dict] = []
    while chunks:
        if len(chunks) > MAX_CHUNKS:
            log(f"WARN {address}: chunk budget exhausted, some fills skipped")
            break
        s, e = chunks.pop(0)
        fills = api_post({"type": "userFillsByTime", "user": address,
                          "startTime": int(s), "endTime": int(e)})
        if not isinstance(fills, list):
            fills = []
        if len(fills) >= MAX_FILLS_PER_CHUNK and e - s > 60000:
            mid = (s + e) // 2
            chunks.insert(0, (s, mid))
            chunks.insert(1, (mid, e))
        else:
            if len(fills) >= MAX_FILLS_PER_CHUNK:
                log(f"WARN {address}: dense 60s window hit fill cap")
            out.extend(fills)
    return out


def fetch_mids() -> dict[str, float]:
    raw = api_post({"type": "allMids"})
    mids = {}
    for coin, px in (raw.items() if isinstance(raw, dict) else []):
        try:
            v = float(px)
            if v > 0:
                mids[str(coin)] = v
        except (TypeError, ValueError):
            pass
    return mids


# --------------------------------------------------------------------------
# Scoring (engine logic, adapted for live ms timestamps)
# --------------------------------------------------------------------------
def normalize_for_scorer(fills: list[dict]) -> list[dict]:
    """Adapter: live fills use ms timestamps and `closedPnl`; the engine
    scorer expects seconds and `pnl`. (score_wallet overflows on ms
    timestamps — verified 2026-10-02 — so this normalization is load-
    bearing, not cosmetic.)"""
    out = []
    for f in fills:
        try:
            ts_ms = float(f.get("time", 0) or 0)
        except (TypeError, ValueError):
            continue
        out.append({"coin": str(f.get("coin", "")),
                    "dir": str(f.get("dir", "")),
                    "sz": str(f.get("sz", "0")),
                    "px": str(f.get("px", "0")),
                    "time": ts_ms / 1000.0,
                    "pnl": float(f.get("closedPnl") or 0.0),
                    "hash": str(f.get("hash", ""))})
    return out


def score_target_fills(fills: list[dict]):
    """-> (score, classification, closed_count, recent_closes_usd)."""
    norm = normalize_for_scorer(fills)
    stats = score_wallet(norm, SCORER_WEIGHTS, min_closed=MIN_CLOSED)
    cls, _watch = classify(stats["score"], stats["closed"], MIN_CLOSED,
                           MIRROR_SCORE, FADE_SCORE,
                           flow_flags=stats.get("flow_flags"))
    closes = realized_closes(norm)
    recent = [c["pnl_usd"] for c in closes[-50:]]
    return stats["score"], cls, stats["closed"], recent


# --------------------------------------------------------------------------
# Copy decision + intents
# --------------------------------------------------------------------------
def decide_copy(tstate: dict, coin: str, intent_px: float):
    """-> (size_usd | None, reason). The copy gate."""
    if tstate.get("classification") != "copy":
        return None, (f"skip: target {tstate.get('classification')} "
                      f"(score {tstate.get('score', 0):.1f})")
    if coin in COIN_BLOCKLIST:
        return None, f"skip: {coin} blocklisted (no copy edge in backtest)"
    wf = tstate.get("paper_pnl_window", [])
    if len(wf) >= WF_PAUSE_MIN_TRADES and sum(wf) < 0:
        return None, (f"skip: walk-forward paused "
                      f"(trailing {len(wf)} paper trades {sum(wf):+.2f} USD)")
    if intent_px <= 0:
        return None, "skip: no price"
    f = kelly_fstar(tstate.get("recent_closes_usd", []), KELLY_MIN_CLOSES)
    base = RISK_PCT * EQUITY_USD
    if f is not None and f <= 0:
        return None, "skip: kelly_negative_edge"
    cap = base if f is None else min(base, f * KELLY_FRACTION * base)
    if cap < MIN_NOTIONAL_USD:
        return None, f"skip: size ${cap:.2f} below ${MIN_NOTIONAL_USD:.0f} min"
    kelly_txt = "unmeasured" if f is None else f"f*={f:.3f}"
    return cap, f"ok ({kelly_txt})"


def dir_class(d: str) -> str | None:
    if d.startswith("Open"):
        return "open"
    if d.startswith("Close"):
        return "close"
    return None


def aggregate_intents(fills: list[dict]) -> list[dict]:
    """Group a target's fragmented fills into intents: same coin +
    same open/close class within INTENT_WINDOW_S -> one intent
    (total size, size-weighted px). Closes are NOT aggregated (each
    close fill carries its own startPosition for proportional math)."""
    intents: list[dict] = []
    ordered = sorted(fills, key=lambda f: (float(f.get("time", 0) or 0),
                                           int(f.get("tid", 0) or 0)))
    for f in ordered:
        coin = str(f.get("coin", ""))
        dc = dir_class(str(f.get("dir", "")))
        if not coin or dc is None:
            continue
        if dc == "close":
            intents.append({"kind": "close", "coin": coin, "fill": f,
                            "time": float(f.get("time", 0) or 0)})
            continue
        t = float(f.get("time", 0) or 0)
        sz = abs(float(f.get("sz", 0) or 0))
        px = float(f.get("px", 0) or 0)
        if sz <= 0 or px <= 0:
            continue
        if (intents and intents[-1].get("kind") == "open"
                and intents[-1]["coin"] == coin
                and intents[-1]["dir"] == str(f.get("dir", ""))
                and t - intents[-1]["time"] <= INTENT_WINDOW_S * 1000):
            it = intents[-1]
            tot = it["sz"] + sz
            it["px"] = (it["px"] * it["sz"] + px * sz) / tot
            it["sz"] = tot
            it["time"] = t
            it["hashes"].append(str(f.get("hash", "")))
            it["fragment_count"] += 1
        else:
            intents.append({"kind": "open", "coin": coin,
                            "dir": str(f.get("dir", "")),
                            "side": "long" if "Long" in str(f.get("dir", ""))
                            else "short",
                            "sz": sz, "px": px, "time": t,
                            "hashes": [str(f.get("hash", ""))],
                            "fragment_count": 1})
    return intents


# --------------------------------------------------------------------------
# Paper ledger helpers
# --------------------------------------------------------------------------
def equity_usd(state: dict) -> float:
    return EQUITY_USD + state.get("realized_pnl_usd", 0.0)


def open_position(state: dict, target: dict, intent: dict, size_usd: float,
                  reason: str, rows: list[dict]) -> None:
    coin, side, px = intent["coin"], intent["side"], intent["px"]
    t = intent["time"]
    size_coin = size_usd / px
    fee = size_usd * FEE_SIDE
    pid = state["next_id"]
    state["next_id"] += 1
    pos = {"id": pid, "target": target["address"], "label": target["label"],
           "coin": coin, "side": side,
           "size": size_coin if side == "long" else -size_coin,
           "entry_px": px, "entry_ts": t / 1000.0, "peak_fav_pct": 0.0,
           "notional_usd": size_usd, "fee_open_usd": fee,
           "orig_size": size_coin}
    state["positions"].append(pos)
    state["fees_paid_usd"] = state.get("fees_paid_usd", 0.0) + fee
    rows.append({"ts": int(t), "target": target["label"], "coin": coin,
                 "side": side, "action": "open",
                 "size": round(size_coin, 8), "price": px,
                 "fee_usd": round(fee, 4), "realized_pnl_usd": "",
                 "paper_equity_usd": round(equity_usd(state), 2),
                 "reason": f"{reason} frags={intent['fragment_count']}",
                 "fill_hash": ";".join(intent["hashes"])})
    log(f"OPEN {target['label']} {coin} {side} {size_coin:.6f} @ {px} "
        f"(${size_usd:.0f}, {reason})")


def close_position(state: dict, pos: dict, exit_px: float, exit_ts_ms: float,
                   reason: str, pct: float, rows: list[dict],
                   fill_hash: str = "") -> None:
    held = abs(pos["size"])
    if held <= 0 or exit_px <= 0:
        return
    close_coin = held * min(max(pct, 0.0), 1.0)
    # avoid dust remnants
    if 0 < held - close_coin and (held - close_coin) * exit_px < 1.0:
        close_coin = held
    sign = 1 if pos["size"] > 0 else -1
    gross = (exit_px - pos["entry_px"]) * sign * close_coin
    fee_close = close_coin * exit_px * FEE_SIDE
    fee_open_attr = pos.get("fee_open_usd", 0.0) * (close_coin / pos["orig_size"]
                                                   if pos.get("orig_size") else 0)
    realized = gross - fee_open_attr - fee_close
    state["realized_pnl_usd"] = state.get("realized_pnl_usd", 0.0) + realized
    state["fees_paid_usd"] = state.get("fees_paid_usd", 0.0) + fee_close
    # walk-forward: per-target trailing paper-PnL window
    tgt = state["targets"].get(pos.get("target", ""), None)
    if tgt is not None:
        w = tgt.setdefault("paper_pnl_window", [])
        w.append(round(realized, 4))
        del w[:-WF_PAUSE_WINDOW]
        tgt["paper_pnl_usd"] = round(tgt.get("paper_pnl_usd", 0.0) + realized, 4)
    pos["fee_open_usd"] = pos.get("fee_open_usd", 0.0) - fee_open_attr
    pos["size"] = sign * (held - close_coin)
    rows.append({"ts": int(exit_ts_ms), "target": pos["label"],
                 "coin": pos["coin"], "side": pos["side"], "action": reason,
                 "size": round(close_coin, 8), "price": exit_px,
                 "fee_usd": round(fee_close, 4),
                 "realized_pnl_usd": round(realized, 4),
                 "paper_equity_usd": round(equity_usd(state), 2),
                 "reason": f"pct={pct:.2f}", "fill_hash": fill_hash})
    log(f"CLOSE {pos['label']} {pos['coin']} {pct*100:.0f}% @ {exit_px} "
        f"reason={reason} pnl {realized:+.2f} USD")
    if abs(pos["size"]) * exit_px < 1.0:
        state["positions"].remove(pos)


def find_position(state: dict, target_addr: str, coin: str):
    for p in state["positions"]:
        if p["target"] == target_addr and p["coin"] == coin:
            return p
    return None


# --------------------------------------------------------------------------
# Per-target processing
# --------------------------------------------------------------------------
def refresh_score(state: dict, target: dict, now_s: float) -> None:
    addr = target["address"]
    ts = state["targets"].setdefault(
        addr, {"label": target["label"], "kind": target["kind"],
               "watermark_time": 0, "seen_hashes": [],
               "score": 0.0, "classification": "pass", "closed": 0,
               "recent_closes_usd": [], "last_scored": 0})
    if now_s - ts.get("last_scored", 0) < SCORE_TTL_S and ts.get("last_scored"):
        return
    end_ms = int(now_s * 1000)
    start_ms = end_ms - SCORE_LOOKBACK_DAYS * 86400 * 1000
    fills = fetch_fills_window(addr, start_ms, end_ms)
    # cap scoring input for very busy vaults
    fills = fills[-30000:]
    score, cls, closed, recent = score_target_fills(fills)
    ts.update({"score": score, "classification": cls, "closed": closed,
               "recent_closes_usd": recent, "last_scored": now_s,
               "label": target["label"], "kind": target["kind"]})
    log(f"SCORE {target['label']}: {cls} score={score:.1f} closed={closed} "
        f"({len(fills)} fills scored)")


def process_target(target: dict, state: dict, rows: list[dict],
                   now_ms: int) -> None:
    addr = target["address"]
    ts = state["targets"][addr]
    seen = set(ts.get("seen_hashes", []))

    wm = ts.get("watermark_time") or now_ms  # first run: no backfill
    if not ts.get("watermark_time"):
        ts["watermark_time"] = now_ms
        log(f"{target['label']}: first run, watermark set to now "
            f"(no historical backfill)")
    start_ms = max(wm, now_ms - MAX_LOOKBACK_S * 1000)
    fills = fetch_fills_window(addr, start_ms, now_ms)

    fresh, max_t = [], wm
    for f in fills:
        h = str(f.get("hash", ""))
        if not h or h in seen:
            continue
        try:
            t = int(float(f.get("time", 0) or 0))
        except (TypeError, ValueError):
            continue
        seen.add(h)
        max_t = max(max_t, t)
        if t <= now_ms - STALE_CUTOFF_S * 1000:
            continue  # too old to copy; marked seen, watermark advances
        d = str(f.get("dir", ""))
        if d == "Settlement":
            continue
        if not d.startswith(("Open", "Close")):
            log(f"WARN {target['label']}: ambiguous dir {d!r} on "
                f"{f.get('coin')}; treating as open per policy")
        fresh.append(f)

    intents = aggregate_intents(fresh)
    n_open = n_close = 0
    for it in intents:
        if it["kind"] == "open":
            n_open += 1
            handle_open(target, ts, it, state, rows)
        else:
            n_close += 1
            handle_close(target, it["fill"], state, rows)

    ts["seen_hashes"] = list(seen)[-SEEN_CAP:]
    ts["watermark_time"] = max_t
    log(f"{target['label']}: {len(fills)} fills fetched, "
        f"{len(fresh)} new, {n_open} open-intents, {n_close} closes")


def handle_open(target: dict, ts: dict, intent: dict, state: dict,
                rows: list[dict]) -> None:
    addr = target["address"]
    coin = intent["coin"]
    if find_position(state, addr, coin):
        log(f"SKIP {target['label']} {coin}: already_positioned")
        return
    size_usd, reason = decide_copy(ts, coin, intent["px"])
    if size_usd is None:
        log(f"SKIP {target['label']} {coin} {intent['side']} @ "
            f"{intent['px']}: {reason}")
        return
    open_position(state, target, intent, size_usd, reason, rows)


def handle_close(target: dict, fill: dict, state: dict,
                 rows: list[dict]) -> None:
    addr = target["address"]
    coin = str(fill.get("coin", ""))
    pos = find_position(state, addr, coin)
    if pos is None:
        log(f"SKIP {target['label']} {coin} close: no_open_position")
        return
    try:
        sp = abs(float(fill.get("startPosition") or 0))
        sz = abs(float(fill.get("sz") or 0))
    except (TypeError, ValueError):
        sp, sz = 0.0, 0.0
    pct = min(sz / sp, 1.0) if sp > 0 else 1.0
    px = float(fill.get("px", 0) or 0)
    if px <= 0:
        log(f"SKIP {target['label']} {coin} close: no price")
        return
    close_position(state, pos, px, float(fill.get("time", 0) or 0),
                   "target_exit", pct, rows,
                   fill_hash=str(fill.get("hash", "")))


# --------------------------------------------------------------------------
# Independent exits (exits.py logic, trailing peak persisted in state)
# --------------------------------------------------------------------------
def evaluate_exits(state: dict, mids: dict[str, float], now_s: float,
                   rows: list[dict]) -> None:
    for pos in list(state["positions"]):
        mark = mids.get(pos["coin"])
        if not mark or mark <= 0:
            log(f"WARN no mark for {pos['coin']}; holding (never guess)")
            continue
        entry = pos["entry_px"]
        fav = ((mark / entry - 1.0) * 100.0 if pos["size"] > 0
               else (entry / mark - 1.0) * 100.0)
        pos["peak_fav_pct"] = max(pos.get("peak_fav_pct", 0.0), fav)
        reason = None
        if fav <= -STOP_LOSS_PCT:
            reason = "stop"
        elif (TRAILING_PCT > 0 and pos["peak_fav_pct"] > 0
              and fav <= pos["peak_fav_pct"] - TRAILING_PCT):
            reason = "trailing"
        elif fav >= TAKE_PROFIT_PCT:
            reason = "tp"
        elif now_s - pos["entry_ts"] >= MAX_HOLD_S:
            reason = "maxhold"
        if reason:
            close_position(state, pos, mark, now_s * 1000, reason, 1.0,
                           rows)


# --------------------------------------------------------------------------
# Output: CSV + summary
# --------------------------------------------------------------------------
def append_csv(rows: list[dict]) -> None:
    if not rows:
        return
    new_file = not os.path.exists(CSV_PATH)
    with open(CSV_PATH, "a", newline="") as f:
        if new_file:
            for line in CSV_PREAMBLE:
                f.write(line + "\n")
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        if new_file:
            w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in CSV_FIELDS})


def rebuild_summary(state: dict) -> None:
    per_target: dict[str, dict] = {}
    wins = losses = trades = 0
    realized = fees = 0.0
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, newline="") as f:
            lines = [ln for ln in f if not ln.startswith("#")]
        reader = csv.DictReader(lines)
        for row in reader:
            if row.get("action") in ("open",):
                continue
            try:
                pnl = float(row.get("realized_pnl_usd") or 0)
                fee = float(row.get("fee_usd") or 0)
            except (TypeError, ValueError):
                continue
            trades += 1
            realized += pnl
            fees += fee
            if pnl > 0:
                wins += 1
            elif pnl < 0:
                losses += 1
            t = per_target.setdefault(
                row.get("target", "?"),
                {"trades": 0, "wins": 0, "losses": 0,
                 "realized_pnl_usd": 0.0, "fees_usd": 0.0})
            t["trades"] += 1
            t["realized_pnl_usd"] += pnl
            t["fees_usd"] += fee
            if pnl > 0:
                t["wins"] += 1
            elif pnl < 0:
                t["losses"] += 1
    summary = {
        "updated_ts": datetime.now(timezone.utc).isoformat(),
        "paper_equity_usd": round(EQUITY_USD + realized, 2),
        "realized_pnl_usd": round(realized, 2),
        "fees_paid_usd": round(fees, 2),
        "closed_trades": trades, "wins": wins, "losses": losses,
        "open_positions": [
            {"target": p["label"], "coin": p["coin"], "side": p["side"],
             "size": p["size"], "entry_px": p["entry_px"]}
            for p in state["positions"]],
        "per_target": {k: {**v, "realized_pnl_usd": round(v["realized_pnl_usd"], 2),
                           "fees_usd": round(v["fees_usd"], 2)}
                       for k, v in per_target.items()},
        "target_scores": {t["label"]: {
            "score": round(s.get("score", 0.0), 1),
            "classification": s.get("classification", "?"),
            "closed": s.get("closed", 0)}
            for addr, s in state["targets"].items()
            for t in [{"label": s.get("label", addr)}]},
        "assumptions": {
            "fee_per_side_pct": round(FEE_SIDE * 100, 4),
            "paper_equity_usd": EQUITY_USD,
            "risk_per_position_pct": RISK_PCT * 100,
            "mirror_score_threshold": MIRROR_SCORE,
            "min_closed_trades": MIN_CLOSED,
            "stops_pct": {"stop_loss": STOP_LOSS_PCT,
                          "take_profit": TAKE_PROFIT_PCT,
                          "trailing": TRAILING_PCT},
            "max_hold_hours": MAX_HOLD_S / 3600,
        },
    }
    tmp = SUMMARY_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(summary, f, indent=1)
    os.replace(tmp, SUMMARY_PATH)


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def main() -> int:
    t0 = time.time()
    log("=== paper_tracker run start ===")
    state = load_state()
    state["run_count"] = state.get("run_count", 0) + 1
    targets = load_targets()
    if not targets:
        log("no real targets yet — add vault addresses to paper_targets.json")
        rebuild_summary(state)
        save_state(state)
        log("=== run end (no targets) ===")
        return 0

    now_ms = int(time.time() * 1000)
    now_s = now_ms / 1000.0
    rows: list[dict] = []

    try:
        mids = fetch_mids()
    except Exception as e:
        log(f"ERROR fetching mids: {e}; exits will hold this run")
        mids = {}

    for t in targets:
        try:
            refresh_score(state, t, now_s)
        except Exception:
            log(f"ERROR scoring {t['label']}: {traceback.format_exc(limit=3)}")
        try:
            process_target(t, state, rows, now_ms)
        except Exception:
            log(f"ERROR processing {t['label']}: {traceback.format_exc(limit=3)}")

    try:
        evaluate_exits(state, mids, now_s, rows)
    except Exception:
        log(f"ERROR in exits: {traceback.format_exc(limit=3)}")

    append_csv(rows)
    save_state(state)  # atomic; after CSV so reruns dedup by fill hash
    rebuild_summary(state)
    dt = time.time() - t0
    log(f"=== run end: {len(rows)} rows, {len(state['positions'])} open, "
        f"equity ${equity_usd(state):,.2f} in {dt:.1f}s ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
