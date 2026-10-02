#!/usr/bin/env python3
"""Historical backtest of the Hyperliquid copy engine (30d, real mainnet).

Replays each target vault's fills chronologically through the engine's
copy logic and reports whether the gated copy strategy shows edge:

  * rolling daily score per vault (exact engine scorer, trailing-30d
    history): copy only when score >= 65 AND >= 10 closed trades;
  * entries at the target's actual fill price, fragmented fills
    aggregated to one intent per (coin, direction) within 60s;
  * size = min(2% of $10k paper equity, fractional-Kelly cap from the
    target's measured edge); skipped entirely when Kelly edge <= 0;
  * exits: (a) proportional closes when the target closes
    (closePct = fill.sz / |startPosition| at the target's fill price);
    (b) independent SL 8% / TP 20% / trailing 2% / max-hold 24h
    evaluated on 15m historical candles (conservative: stops fill at
    the stop level; SL wins ties within one candle);
  * costs: taker fee 0.035% + slippage 0.02% PER SIDE on every fill.

Signals the gate rejects (score too low / too few closes / Kelly
negative) are tracked as SHADOW trades (naive $200 copy, exits on
target closes or 24h max-hold) so the gated strategy can be compared
against "copy everything".

ASSUMPTIONS / LIMITATIONS (read before quoting the numbers):
  * full fills at historical prices; no market impact;
  * exits evaluated on 15m candle closes — finer than the live
    tracker's 30-min cadence, so stops may trigger slightly more;
  * same-candle SL+TP touch resolves to the stop (conservative);
  * no funding payments modeled; no borrow costs;
  * paper equity is fixed at $10k (no compounding), one paper
    position per (vault, coin) — identical to paper_tracker.py;
  * Kelly edge uses per-day closes (stale within the day);
  * shadow exits are simplified (no stops/trailing).

Stdlib only.
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
except ImportError as e:
    print(f"FATAL: cannot import engine modules from {ENGINE_DIR}: {e}",
          file=sys.stderr)
    sys.exit(1)

# --------------------------------------------------------------------------
# Constants (mirror paper_tracker.py)
# --------------------------------------------------------------------------
BASE_DIR = os.path.expanduser("~/workspace/copy-trading")
# Tuning variants (set VARIANT env var to "A" or "B"); baseline uses
# backtest.py untouched. Variant A: trailing stop disabled.
# Variant B: trailing disabled + Kelly fraction doubled (0.25 -> 0.5).
_VARIANT = os.environ.get("VARIANT", "A").upper()
VARIANT_LABEL = {
    "A": "no-trailing (SL 8% / TP 20% / 24h max-hold only)",
    "B": "no-trailing + kelly_fraction 0.5",
}.get(_VARIANT, "no-trailing")
CSV_PATH = os.path.join(BASE_DIR, f"backtest_tuned_{_VARIANT}_trades.csv")
SUMMARY_PATH = os.path.join(BASE_DIR, f"backtest_tuned_{_VARIANT}_summary.json")
LOG_PATH = os.path.join(BASE_DIR, "backtest_tuned.log")

TARGETS = [
    ("0x00ae7dc3e9796260506afe8fdb0598c281f10776", "winning-fortunes"),
    ("0xa1222c3590709cd9bce80ae04c2fd07e89e8ab2a", "GeorgV Copytrading"),
    ("0xa2ec76b6464bcbd771f11b769d40055176a6e4a3", "Kairos Fi"),
    ("0x50e2fe552727a4b8692c192b4f96d1a6b0d44394", "Aquila Chrysaetos"),
]

INFO_URL = "https://api.hyperliquid.xyz/info"
HTTP_TIMEOUT = 30
PACE_S = 0.2  # polite pacing between API calls

EQUITY_USD = 10000.0
RISK_PCT = 0.02
BASE_SIZE_USD = RISK_PCT * EQUITY_USD   # $200
# Variant B doubles the Kelly fraction (0.25 -> 0.5): a pure linear scale
# on the Kelly cap. Chosen over lowering the edge floor because it keeps
# the skip-on-negative-edge logic intact while directly addressing
# starved position sizes. Env override keeps one script for both runs.
KELLY_FRACTION = float(os.environ.get("KELLY_FRACTION",
                                      "0.5" if _VARIANT == "B" else "0.25"))
KELLY_MIN_CLOSES = 10
MIN_NOTIONAL_USD = 10.0
SHADOW_SIZE_USD = 200.0                 # naive copy size for shadows

FEE_SIDE = 0.00035 + 0.00020           # taker + slippage per side

MIRROR_SCORE = 65.0
FADE_SCORE = 30.0
MIN_CLOSED = 10
INTENT_WINDOW_MS = 60_000

STOP_LOSS_PCT = 8.0
TAKE_PROFIT_PCT = 20.0
TRAILING_PCT = 2.0
# Tuning variants disable the trailing stop entirely: the baseline found
# it was the dominant independent exit (179/775 legs) and evidence
# suggests it cuts winners short. Env override for flexibility.
ENABLE_TRAILING = os.environ.get("TRAILING_ENABLED", "0") == "1"
MAX_HOLD_MS = 24 * 3600 * 1000

SCORE_HISTORY_DAYS = 60   # fills fetched for scoring history
TRADE_WINDOW_DAYS = 30    # fills actually traded in the backtest
SCORE_TRAIL_DAYS = 30     # trailing window the scorer sees per day

MAX_FILLS_PER_CHUNK = 1990
MAX_CHUNKS = 128

SCORER_WEIGHTS = {"win_rate": 25, "profit_factor": 20, "consistency": 15,
                  "max_drawdown": 15, "sample_size": 15, "recency": 10}

CSV_FIELDS = ["vault", "coin", "side", "kind", "entry_ts", "exit_ts",
              "entry_px", "exit_px", "qty", "pnl_gross_usd", "fees_usd",
              "pnl_net_usd", "exit_reason", "hold_h"]

CSV_PREAMBLE = [
    "# backtest_tuned.py — tuning variants of the 30d copy-engine backtest",
    "# kind=paper: gated copy (score>=65, >=10 closes, Kelly sizing).",
    "# kind=shadow: every rejected signal copied naively at $200, exits on",
    "#   target closes or 24h max-hold (no stops/trailing).",
    "# ASSUMPTIONS: full fills at historical prices; no market impact;",
    "#   exits on 15m candles (finer than live 30-min cadence); same-candle",
    "#   SL+TP touch resolves to the stop; no funding modeled.",
    "# COSTS: taker 0.035% + slippage 0.02% per side on every fill.",
]


def log(msg: str) -> None:
    line = f"{datetime.now(timezone.utc):%Y-%m-%dT%H:%M:%SZ} {msg}"
    print(line, flush=True)
    try:
        with open(LOG_PATH, "a") as f:
            f.write(line + "\n")
    except OSError:
        pass


# --------------------------------------------------------------------------
# Hyperliquid public API
# --------------------------------------------------------------------------
def api_post(payload: dict):
    data = json.dumps(payload).encode()
    last: Exception | None = None
    for attempt in (1, 2, 3):
        try:
            req = urllib.request.Request(
                INFO_URL, data=data,
                headers={"Content-Type": "application/json",
                         "User-Agent": "copy-backtest/0.1"})
            with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as r:
                time.sleep(PACE_S)
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < 3:
                time.sleep(2 ** attempt * 2)
                continue
            raise
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            last = e
            if attempt < 3:
                time.sleep(2 ** attempt * 2)
                continue
            raise
    raise RuntimeError(f"unreachable: {last}")


def fetch_fills_window(address: str, start_ms: int, end_ms: int) -> list[dict]:
    """All fills in [start_ms, end_ms], splitting dense windows."""
    chunks = [(start_ms, end_ms)]
    out: list[dict] = []
    while chunks:
        if len(chunks) > MAX_CHUNKS:
            log(f"WARN {address}: chunk budget exhausted, fills skipped")
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


def fetch_candles(coin: str, start_ms: int, end_ms: int) -> list[dict]:
    """15m candles for a coin; normalized to dicts with T,o,h,l,c (floats)."""
    raw = api_post({"type": "candleSnapshot",
                    "req": {"coin": coin, "interval": "15m",
                            "startTime": int(start_ms),
                            "endTime": int(end_ms)}})
    out = []
    if not isinstance(raw, list):
        return out
    for c in raw:
        if not isinstance(c, dict):
            continue
        try:
            t = int(float(c.get("T", c.get("t", 0)) or 0))
            o = float(c.get("o", 0) or 0)
            h = float(c.get("h", 0) or 0)
            l = float(c.get("l", 0) or 0)
            cl = float(c.get("c", 0) or 0)
        except (TypeError, ValueError):
            continue
        if t <= 0 or cl <= 0:
            continue
        out.append({"T": t, "o": o, "h": h, "l": l, "c": cl})
    out.sort(key=lambda c: c["T"])
    return out

# --------------------------------------------------------------------------
# Fill helpers + intent aggregation
# --------------------------------------------------------------------------
def fill_time_ms(f: dict) -> int:
    try:
        return int(float(f.get("time", 0) or 0))
    except (TypeError, ValueError):
        return 0


def fill_dir(f: dict) -> str:
    return str(f.get("dir", ""))


def dir_class(d: str) -> str | None:
    if d.startswith("Open"):
        return "open"
    if d.startswith("Close"):
        return "close"
    return None


def fill_side(f: dict) -> str:
    return "long" if "Long" in fill_dir(f) else "short"


def signed_size(f: dict) -> float:
    """Signed size from the target's perspective (for position tracking)."""
    try:
        sz = abs(float(f.get("sz", 0) or 0))
    except (TypeError, ValueError):
        return 0.0
    d = fill_dir(f)
    if d.startswith("Open"):
        return sz if "Long" in d else -sz
    if d.startswith("Close"):
        return -sz if "Long" in d else sz
    return 0.0


def aggregate_open_intents(fills: list[dict]) -> list[dict]:
    """Group fragmented open fills into intents: same coin + same dir
    within INTENT_WINDOW_MS -> one intent (total size, size-weighted px)."""
    intents: list[dict] = []
    ordered = sorted(fills, key=lambda f: (fill_time_ms(f),
                                           int(f.get("tid", 0) or 0)))
    for f in ordered:
        coin = str(f.get("coin", ""))
        d = fill_dir(f)
        if dir_class(d) != "open" or not coin:
            continue
        try:
            t = fill_time_ms(f)
            sz = abs(float(f.get("sz", 0) or 0))
            px = float(f.get("px", 0) or 0)
        except (TypeError, ValueError):
            continue
        if sz <= 0 or px <= 0 or t <= 0:
            continue
        if (intents and intents[-1]["coin"] == coin
                and intents[-1]["dir"] == d
                and t - intents[-1]["time"] <= INTENT_WINDOW_MS):
            it = intents[-1]
            tot = it["sz"] + sz
            it["px"] = (it["px"] * it["sz"] + px * sz) / tot
            it["sz"] = tot
            it["time"] = t
            it["frags"] += 1
        else:
            intents.append({"coin": coin, "dir": d, "side": fill_side(f),
                            "sz": sz, "px": px, "time": t, "frags": 1})
    return intents


def close_fills_for(fills: list[dict]) -> list[dict]:
    """Target close fills, each annotated with the target's position in
    that coin just before the fill (for proportional close math)."""
    ordered = sorted(fills, key=lambda f: (fill_time_ms(f),
                                           int(f.get("tid", 0) or 0)))
    pos: dict[str, float] = {}
    out = []
    for f in ordered:
        coin = str(f.get("coin", ""))
        d = fill_dir(f)
        if not coin or d == "Settlement":
            continue
        if dir_class(d) == "close":
            try:
                sz = abs(float(f.get("sz", 0) or 0))
                px = float(f.get("px", 0) or 0)
                t = fill_time_ms(f)
            except (TypeError, ValueError):
                continue
            if sz <= 0 or px <= 0 or t <= 0:
                continue
            sp = f.get("startPosition")
            try:
                start_pos = abs(float(sp)) if sp is not None else abs(
                    pos.get(coin, 0.0))
            except (TypeError, ValueError):
                start_pos = abs(pos.get(coin, 0.0))
            pct = min(sz / start_pos, 1.0) if start_pos > 0 else 1.0
            out.append({"coin": coin, "time": t, "sz": sz, "px": px,
                        "pct": pct})
        pos[coin] = pos.get(coin, 0.0) + signed_size(f)
    return out


# --------------------------------------------------------------------------
# Sizing (mirror paper_tracker.decide_copy)
# --------------------------------------------------------------------------
def decide_size(recent_closes_usd: list[float]) -> tuple[float | None, str]:
    f = kelly_fstar(recent_closes_usd, KELLY_MIN_CLOSES)
    if f is not None and f <= 0:
        return None, "skip: kelly_negative_edge"
    cap = BASE_SIZE_USD if f is None else min(
        BASE_SIZE_USD, f * KELLY_FRACTION * BASE_SIZE_USD)
    if cap < MIN_NOTIONAL_USD:
        return None, f"skip: size ${cap:.2f} below min"
    return cap, f"ok (kelly {'unmeasured' if f is None else f'f*={f:.3f}'})"


# --------------------------------------------------------------------------
# Exit evaluation on candles
# --------------------------------------------------------------------------
def candle_exit(side: str, entry_px: float, entry_t: int, peak_fav: float,
                c: dict) -> tuple[str, float, float] | None:
    """-> (reason, exit_px, new_peak) or None. SL wins same-candle ties."""
    sl_mult = 1 - STOP_LOSS_PCT / 100.0
    tp_mult = 1 + TAKE_PROFIT_PCT / 100.0
    if side == "long":
        if c["l"] <= entry_px * sl_mult:
            return "stop", entry_px * sl_mult, peak_fav
        if c["h"] >= entry_px * tp_mult:
            return "tp", entry_px * tp_mult, peak_fav
        fav = (c["c"] / entry_px - 1.0) * 100.0
    else:
        if c["h"] >= entry_px * (2 - sl_mult):
            return "stop", entry_px * (2 - sl_mult), peak_fav
        if c["l"] <= entry_px * (2 - tp_mult):
            return "tp", entry_px * (2 - tp_mult), peak_fav
        fav = (entry_px / c["c"] - 1.0) * 100.0
    peak = max(peak_fav, fav)
    if ENABLE_TRAILING and peak > 0 and fav <= peak - TRAILING_PCT:
        trail_mult = ((1 + (peak - TRAILING_PCT) / 100.0) if side == "long"
                      else (1 - (peak - TRAILING_PCT) / 100.0))
        return "trailing", entry_px * trail_mult, peak
    if c["T"] >= entry_t + MAX_HOLD_MS:
        return "maxhold", c["c"], peak
    return None


def close_trade_row(vault: str, coin: str, side: str, kind: str,
                    entry_t: int, exit_t: int, entry_px: float,
                    exit_px: float, qty: float, fee_entry: float,
                    reason: str) -> dict:
    sign = 1 if side == "long" else -1
    gross = (exit_px - entry_px) * sign * qty
    fee_exit = qty * exit_px * FEE_SIDE
    net = gross - fee_entry - fee_exit
    hold_h = (exit_t - entry_t) / 3600000.0
    return {"vault": vault, "coin": coin, "side": side, "kind": kind,
            "entry_ts": entry_t, "exit_ts": exit_t,
            "entry_px": entry_px, "exit_px": exit_px, "qty": qty,
            "pnl_gross_usd": round(gross, 4),
            "fees_usd": round(fee_entry + fee_exit, 4),
            "pnl_net_usd": round(net, 4), "exit_reason": reason,
            "hold_h": round(hold_h, 2)}


def run_paper_position(vault: str, intent: dict, size_usd: float,
                       target_closes: list[dict],
                       candles: list[dict]) -> list[dict]:
    """Full lifecycle of one gated paper position. Returns trade rows."""
    coin, side = intent["coin"], intent["side"]
    entry_px, entry_t = intent["px"], intent["time"]
    size_coin = size_usd / entry_px
    fee_entry_total = size_usd * FEE_SIDE
    remaining = size_coin
    peak = 0.0
    rows: list[dict] = []

    # merged event stream: target closes + candles after entry
    tcloses = [c for c in target_closes
               if c["coin"] == coin and c["time"] > entry_t]
    cands = [c for c in candles if c["T"] >= entry_t]
    events = ([("close", c["time"], c) for c in tcloses]
              + [("candle", c["T"], c) for c in cands])
    events.sort(key=lambda e: (e[1], 0 if e[0] == "close" else 1))

    def emit(qty: float, exit_px: float, exit_t: int, reason: str):
        nonlocal remaining
        attr = fee_entry_total * (qty / size_coin) if size_coin else 0.0
        rows.append(close_trade_row(
            vault, coin, side, "paper", entry_t, exit_t, entry_px,
            exit_px, qty, attr, reason))
        remaining -= qty

    for kind, t, payload in events:
        if remaining <= 0:
            break
        if kind == "close":
            q = remaining * payload["pct"]
            if 0 < remaining - q and (remaining - q) * payload["px"] < 1.0:
                q = remaining  # dust remnant
            if q > 0:
                emit(q, payload["px"], payload["time"], "target_exit")
        else:
            hit = candle_exit(side, entry_px, entry_t, peak, payload)
            if hit:
                reason, exit_px, peak = hit
                emit(remaining, exit_px, payload["T"], reason)
                break
            # update peak even when no exit fired
            if side == "long":
                fav = (payload["c"] / entry_px - 1.0) * 100.0
            else:
                fav = (entry_px / payload["c"] - 1.0) * 100.0
            peak = max(peak, fav)

    if remaining > 0:  # window ended with size still open
        last = cands[-1] if cands else None
        if last:
            emit(remaining, last["c"], last["T"], "window_end")
        else:
            emit(remaining, entry_px, entry_t, "window_end_noprice")
    return rows


def run_shadow_position(vault: str, intent: dict, target_closes: list[dict],
                        candles: list[dict]) -> list[dict]:
    """Naive copy of a rejected signal: $200, exits IN FULL on the first
    target close after entry, else 24h max-hold at the candle close.
    Exactly one row per signal (no dust-leg explosion). Simplified exits
    (no stops/trailing)."""
    coin, side = intent["coin"], intent["side"]
    entry_px, entry_t = intent["px"], intent["time"]
    size_coin = SHADOW_SIZE_USD / entry_px
    fee_entry = SHADOW_SIZE_USD * FEE_SIDE

    tcloses = [c for c in target_closes
               if c["coin"] == coin and c["time"] > entry_t]
    deadline = entry_t + MAX_HOLD_MS
    cands = [c for c in candles if c["T"] >= entry_t]

    options: list[tuple[int, float, str]] = []
    if tcloses:
        fc = min(tcloses, key=lambda c: c["time"])
        options.append((fc["time"], fc["px"], "target_exit"))
    mh = next((c for c in cands if c["T"] >= deadline), None)
    if mh:
        options.append((mh["T"], mh["c"], "maxhold"))
    elif cands:
        options.append((cands[-1]["T"], cands[-1]["c"], "window_end"))
    else:
        options.append((entry_t, entry_px, "window_end_noprice"))
    exit_t, exit_px, reason = min(options, key=lambda e: e[0])
    return [close_trade_row(vault, coin, side, "shadow", entry_t, exit_t,
                            entry_px, exit_px, size_coin, fee_entry,
                            reason)]

# --------------------------------------------------------------------------
# Per-vault replay
# --------------------------------------------------------------------------
def day_start_ms(ts_ms: int) -> int:
    dt = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
    return int(dt.replace(hour=0, minute=0, second=0,
                          microsecond=0).timestamp() * 1000)


def replay_vault(addr: str, label: str, trade_start: int, trade_end: int,
                 candle_cache: dict[str, list[dict]]) -> dict:
    log(f"--- {label}: fetching fills ---")
    fills = fetch_fills_window(
        addr, trade_start - SCORE_HISTORY_DAYS * 86400000, trade_end)
    fills = [f for f in fills
             if fill_time_ms(f) > 0 and fill_dir(f) != "Settlement"
             and dir_class(fill_dir(f)) in ("open", "close")
             and str(f.get("coin", ""))]
    fills.sort(key=lambda f: (fill_time_ms(f), int(f.get("tid", 0) or 0)))
    log(f"{label}: {len(fills)} fills in scope")

    # per-day rolling score (trailing SCORE_TRAIL_DAYS history)
    day0 = day_start_ms(trade_start)
    days = []
    d = day0
    while d < trade_end:
        days.append(d)
        d += 86400000
    day_gate: dict[int, dict] = {}
    for d in days:
        hist = [f for f in fills
                if d - SCORE_TRAIL_DAYS * 86400000 <= fill_time_ms(f) < d]
        stats = score_wallet(hist, SCORER_WEIGHTS, now_s=d / 1000.0,
                             min_closed=MIN_CLOSED)
        cls, _ = classify(stats["score"], stats["closed"], MIN_CLOSED,
                          MIRROR_SCORE, FADE_SCORE)
        closes = realized_closes(hist)
        recent = [c["pnl_usd"] for c in closes[-50:]]
        day_gate[d] = {"classification": cls, "recent": recent,
                       "score": stats["score"], "closed": stats["closed"]}
    n_copy_days = sum(1 for g in day_gate.values()
                      if g["classification"] == "copy")
    log(f"{label}: gate=open(copy) on {n_copy_days}/{len(days)} days")

    tfills = [f for f in fills if trade_start <= fill_time_ms(f) <= trade_end]
    intents = aggregate_open_intents(tfills)
    tcloses = close_fills_for(tfills)
    log(f"{label}: {len(intents)} open intents, {len(tcloses)} target closes")

    # candles for every coin we might trade
    coins = {i["coin"] for i in intents}
    for coin in sorted(coins):
        if coin not in candle_cache:
            candle_cache[coin] = fetch_candles(
                coin, trade_start - 3600000, trade_end)
            n = len(candle_cache[coin])
            log(f"candles {coin}: {n}")
            if n == 0:
                log(f"WARN no candles for {coin}; its exits fall back to "
                    f"target closes / window end")

    paper_rows: list[dict] = []
    shadow_rows: list[dict] = []
    skipped = 0
    skip_reasons: dict[str, int] = {}
    # open paper positions as (coin, entry_t, final_exit_t); a coin can be
    # re-entered once its position fully closed (mirror tracker's
    # find_position, which only blocks while a position is actually open)
    open_windows: dict[str, list[tuple[int, int]]] = {}

    for it in sorted(intents, key=lambda i: i["time"]):
        coin = it["coin"]
        busy = any(s <= it["time"] < e
                   for (s, e) in open_windows.get(coin, []))
        if busy:
            skip_reasons["already_positioned"] = \
                skip_reasons.get("already_positioned", 0) + 1
            continue
        gate = day_gate[day_start_ms(it["time"])]
        reason = None
        size_usd = None
        if gate["classification"] != "copy":
            reason = (f"gate:{gate['classification']} "
                      f"score={gate['score']:.1f} closed={gate['closed']}")
        else:
            size_usd, why = decide_size(gate["recent"])
            if size_usd is None:
                reason = why
        candles = candle_cache.get(coin, [])
        if reason is None:
            rows = run_paper_position(label, it, size_usd, tcloses, candles)
            if rows:
                exit_t = max(r["exit_ts"] for r in rows)
                open_windows.setdefault(coin, []).append(
                    (it["time"], exit_t))
            paper_rows.extend(rows)
            log(f"PAPER {label} {coin} {it['side']} @ {it['px']} "
                f"(${size_usd:.0f}) -> {len(rows)} exit leg(s)")
        else:
            skipped += 1
            skip_reasons[reason.split()[0]] = \
                skip_reasons.get(reason.split()[0], 0) + 1
            shadow_rows.extend(
                run_shadow_position(label, it, tcloses, candles))

    return {"label": label, "fills": len(fills), "intents": len(intents),
            "paper_rows": paper_rows, "shadow_rows": shadow_rows,
            "skipped": skipped, "skip_reasons": skip_reasons,
            "copy_days": n_copy_days, "total_days": len(days),
            "paper_positions": sum(len(w) for w in open_windows.values())}


# --------------------------------------------------------------------------
# Summary
# --------------------------------------------------------------------------
def summarize(rows: list[dict]) -> dict:
    trades = len(rows)
    wins = sum(1 for r in rows if r["pnl_net_usd"] > 0)
    losses = sum(1 for r in rows if r["pnl_net_usd"] < 0)
    pnl = sum(r["pnl_net_usd"] for r in rows)
    fees = sum(r["fees_usd"] for r in rows)
    # max drawdown on cumulative net-PnL curve (chronological exits)
    eq, peak, dd = 0.0, 0.0, 0.0
    for r in sorted(rows, key=lambda r: r["exit_ts"]):
        eq += r["pnl_net_usd"]
        peak = max(peak, eq)
        if peak > 0:
            dd = max(dd, (peak - eq) / peak)
        elif eq < 0:
            dd = 1.0
    return {"trades": trades, "wins": wins, "losses": losses,
            "win_rate": round(wins / trades, 4) if trades else 0.0,
            "total_pnl_net": round(pnl, 2),
            "total_fees": round(fees, 2),
            "max_drawdown": round(dd, 4)}


def write_csv(rows: list[dict]) -> None:
    with open(CSV_PATH, "w", newline="") as f:
        for line in CSV_PREAMBLE:
            f.write(line + "\n")
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        w.writeheader()
        for r in sorted(rows, key=lambda r: (r["exit_ts"], r["entry_ts"])):
            w.writerow({k: r.get(k, "") for k in CSV_FIELDS})


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def main() -> int:
    t0 = time.time()
    log(f"=== backtest_tuned variant {_VARIANT} start: {VARIANT_LABEL} ===")
    now_ms = int(time.time() * 1000)
    trade_end = now_ms
    trade_start = now_ms - TRADE_WINDOW_DAYS * 86400000
    log(f"trade window: {datetime.fromtimestamp(trade_start/1000, tz=timezone.utc):%Y-%m-%d} "
        f"-> {datetime.fromtimestamp(trade_end/1000, tz=timezone.utc):%Y-%m-%d} UTC; "
        f"scoring history {SCORE_HISTORY_DAYS}d")

    candle_cache: dict[str, list[dict]] = {}
    vault_results = []
    for addr, label in TARGETS:
        try:
            vault_results.append(
                replay_vault(addr, label, trade_start, trade_end,
                             candle_cache))
        except Exception:
            log(f"ERROR replaying {label}: {traceback.format_exc(limit=5)}")

    all_paper = [r for v in vault_results for r in v["paper_rows"]]
    all_shadow = [r for v in vault_results for r in v["shadow_rows"]]
    write_csv(all_paper + all_shadow)

    per_vault = {}
    for v in vault_results:
        s = summarize(v["paper_rows"])
        sh = summarize(v["shadow_rows"])
        per_vault[v["label"]] = {
            **s, "fills_scored": v["fills"], "intents": v["intents"],
            "paper_positions": v["paper_positions"],
            "copy_days": f"{v['copy_days']}/{v['total_days']}",
            "skipped_signals": v["skipped"],
            "skip_reasons": v["skip_reasons"],
            "shadow_trades": sh["trades"],
            "shadow_pnl_net": sh["total_pnl_net"],
            "shadow_win_rate": sh["win_rate"],
        }

    summary = {
        "generated_ts": datetime.now(timezone.utc).isoformat(),
        "variant": _VARIANT,
        "variant_label": VARIANT_LABEL,
        "window_days": TRADE_WINDOW_DAYS,
        "targets": [label for _, label in TARGETS],
        "total": summarize(all_paper),
        "shadow_total": summarize(all_shadow),
        "skipped_signals_total": sum(v["skipped"] for v in vault_results),
        "per_vault": per_vault,
        "assumptions": {
            "fee_per_side_pct": round(FEE_SIDE * 100, 4),
            "paper_equity_usd": EQUITY_USD,
            "base_size_usd": BASE_SIZE_USD,
            "kelly_fraction": KELLY_FRACTION,
            "mirror_score_threshold": MIRROR_SCORE,
            "min_closed_trades": MIN_CLOSED,
            "stops_pct": {"stop_loss": STOP_LOSS_PCT,
                          "take_profit": TAKE_PROFIT_PCT,
                          "trailing": TRAILING_PCT if ENABLE_TRAILING else 0.0,
                          "trailing_enabled": ENABLE_TRAILING},
            "max_hold_hours": MAX_HOLD_MS / 3600000,
            "intent_window_s": INTENT_WINDOW_MS / 1000,
            "candle_interval": "15m",
        },
    }
    with open(SUMMARY_PATH, "w") as f:
        json.dump(summary, f, indent=1)

    tot = summary["total"]
    log(f"=== backtest end in {time.time()-t0:.1f}s: "
        f"{tot['trades']} paper trades, net {tot['total_pnl_net']:+.2f} USD, "
        f"win rate {tot['win_rate']:.1%}, "
        f"shadow net {summary['shadow_total']['total_pnl_net']:+.2f} USD ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
