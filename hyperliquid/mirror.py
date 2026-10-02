#!/usr/bin/env python3
"""Mirror loop for the Hyperliquid copy engine.

Signal: WS `wss://api.hyperliquid.xyz/ws`, subscription `userFills` per
target address. A fill event fires within milliseconds of the target's
fill and carries coin, dir ("Open Long" | "Open Short" | "Close Long" |
"Close Short"), sz, px, startPosition, side — everything the mirror
needs. (Public WS; no auth. Execution is the only part that signs.)

TODO-verify: the exact subscription payload shape and fill field names
against a live WS session before trusting this at scale. The parsing
below is defensive and drops events it cannot understand.

Canonical mirror rules (from the research, encoded here):
  * open:  copySize = fill.sz * multiplier (capped; Kelly shrinks only)
  * close: closePercent = fill.sz / |startPosition|; close the same %
           of our position — stays in sync through partial exits
  * leverage: synced to the target's, capped at config max
  * orders: IOC limit with slippage buffer (behaves like a market order)
  * per-coin serial queues: fills for one coin never race each other
  * intent aggregation: a leader's single entry arrives as many small
           fills; they are grouped by (user, coin, dir) within
           intent_window_s into one intent and copied once
           (Reddit builder, Dwellir). Every fill is deduped by its
           fill hash / trade ID so replays never double-copy.

Live execution is NOT wired: `LiveExecutor.send()` raises
NotImplementedError until the EIP-712 action construction is verified
against Hyperliquid's exchange API. Deployment uses the non-custodial
API-wallet pattern (`approveAgent`: trade-only, cannot withdraw) —
see README.md. Paper mode (paper.py) is the intended mode.
"""
from __future__ import annotations

import json
import queue
import sys
import threading
import time
from datetime import datetime, timezone

EPS = 1e-9


def log(msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"[mirror {ts}] {msg}", file=sys.stderr, flush=True)


# --------------------------------------------------------------------------
# Target-side position book (derived from the fill stream)
# --------------------------------------------------------------------------

class TargetBook:
    """Tracks each target's signed position per coin from fills."""

    def __init__(self):
        self.books: dict[str, dict[str, dict]] = {}  # user -> coin -> state

    def apply(self, fill: dict) -> dict[str, float]:
        """Apply a fill; returns {coin: signed_size} for that user."""
        user = str(fill.get("user", "")).lower()
        coin = str(fill.get("coin", ""))
        direction = str(fill.get("dir", ""))
        sz = abs(float(fill.get("sz", 0) or 0))
        sign = 1 if "Long" in direction else -1
        book = self.books.setdefault(user, {})
        state = book.setdefault(coin, {"size": 0.0})
        if direction.startswith("Open"):
            state["size"] += sign * sz
        elif direction.startswith("Close"):
            if state["size"] > 0:
                state["size"] = max(0.0, state["size"] - sz)
            elif state["size"] < 0:
                state["size"] = min(0.0, state["size"] + sz)
        return {c: s["size"] for c, s in book.items()}

    def position(self, user: str, coin: str) -> float:
        return float(self.books.get(user, {}).get(coin, {}).get("size", 0.0))

    def set_position(self, user: str, coin: str, size: float) -> None:
        """Seed/overwrite a target's position (startup sync)."""
        book = self.books.setdefault(str(user).lower(), {})
        book[str(coin)] = {"size": float(size)}


# --------------------------------------------------------------------------
# Intent aggregation (fill fragmentation)
# --------------------------------------------------------------------------

class IntentAggregator:
    """Group a leader's fragmented fills into one copyable intent.

    A single leader entry routinely arrives as many small fills
    (Reddit builder, Dwellir). Copying per fill misfires — the sizer
    sees each fragment in isolation and the engine spams opens. This
    groups fills by (user, coin, dir) inside a fixed window
    (intent_window_s from the first fill) and emits ONE aggregated
    fill: sz = total, px = size-weighted average, startPosition = the
    last member's (so proportional closes stay correct).

    Dedup: every fill is keyed by its fill hash / trade ID
    (`hash`/`tid`/`trade_id`), falling back to a composite of
    (user, coin, dir, sz, px, ts). Replays and redeliveries are
    dropped before they can touch the book or the sizer.
    """

    def __init__(self, window_s: float):
        self.window_s = float(window_s)
        self.seen: dict[str, float] = {}          # fill id -> ts (pruned)
        self.pending: dict[tuple, dict] = {}      # key -> open intent

    @staticmethod
    def fill_id(fill: dict) -> str:
        h = fill.get("hash") or fill.get("tid") or fill.get("trade_id")
        if h:
            return f"hash:{h}"
        return "cmp:" + "|".join(
            str(fill.get(k, "")) for k in
            ("user", "coin", "dir", "sz", "px", "time", "ts"))

    @staticmethod
    def _key(fill: dict) -> tuple:
        return (str(fill.get("user", "")).lower(),
                str(fill.get("coin", "")),
                str(fill.get("dir", "")))

    @staticmethod
    def _ts(fill: dict) -> float:
        return float(fill.get("time", fill.get("ts", 0)) or 0)

    def _close(self, intent: dict) -> dict:
        fills = sorted(intent["fills"], key=self._ts)
        total = sum(abs(float(f.get("sz", 0) or 0)) for f in fills)
        wpx = (sum(abs(float(f.get("sz", 0) or 0)) * float(f.get("px", 0) or 0)
                   for f in fills) / total) if total > 0 else 0.0
        last = fills[-1]
        user, coin, direction = self._key(last)
        return {
            "user": user, "coin": coin, "dir": direction,
            "sz": total, "px": wpx,
            "startPosition": last.get("startPosition", 0),
            "ts": self._ts(last), "time": self._ts(last),
            "intent": True, "fragment_count": len(fills),
            "fill_ids": [self.fill_id(f) for f in fills],
        }

    def add(self, fill: dict) -> tuple[bool, list[dict]]:
        """Add a fill. -> (is_duplicate, intents closed by rollover)."""
        fid = self.fill_id(fill)
        if fid in self.seen:
            return True, []
        ts = self._ts(fill)
        self.seen[fid] = ts
        key = self._key(fill)
        rolled: list[dict] = []
        it = self.pending.get(key)
        if it is not None and ts - it["first_ts"] > self.window_s:
            rolled.append(self._close(it))
            it = None
        if it is None:
            self.pending[key] = {"fills": [fill], "first_ts": ts}
        else:
            it["fills"].append(fill)
        return False, rolled

    def flush_expired(self, now_ts: float) -> list[dict]:
        """Close intents whose window has elapsed as of now_ts."""
        out: list[dict] = []
        for key in list(self.pending):
            it = self.pending[key]
            if now_ts - it["first_ts"] >= self.window_s:
                out.append(self._close(self.pending.pop(key)))
        # Prune the dedup set: ids older than 10 windows are forgotten.
        cutoff = now_ts - 10 * self.window_s
        for fid in [f for f, t in self.seen.items() if t < cutoff]:
            del self.seen[fid]
        return out

    def flush_all(self) -> list[dict]:
        out = [self._close(self.pending.pop(k)) for k in list(self.pending)]
        return out


# --------------------------------------------------------------------------
# Mirror decision: fill -> actions
# --------------------------------------------------------------------------

def decide_fill(fill: dict, targets: dict, clusters: list[set],
                cluster_votes: dict, cfg: dict,
                risk_ok: callable, sizer: callable) -> list[dict]:
    """Pure decision function -> list of action dicts.

    `risk_ok(coin, notional_usd)` -> (bool, reason).
    `sizer(fill, target)` -> (size_in_coin | None, breakdown).
    Actions: open / close / skip / shadow. Skips also become shadow
    positions in paper mode so the strategy stays improvable.
    """
    user = str(fill.get("user", "")).lower()
    coin = str(fill.get("coin", ""))
    direction = str(fill.get("dir", ""))
    sz = abs(float(fill.get("sz", 0) or 0))
    px = float(fill.get("px", 0) or 0)
    ts = float(fill.get("time", fill.get("ts", 0)) or 0)
    if not user or not coin or sz <= EPS or px <= 0:
        return [{"action": "skip", "reason": "malformed_fill"}]

    target = targets.get(user)
    if target is None:
        return [{"action": "skip", "user": user, "coin": coin,
                 "reason": "unknown_target"}]

    # Single-operator clustering: the cluster casts ONE vote. If this
    # wallet belongs to a cluster, its representative's classification
    # decides, and sizing happens once per cluster signal.
    vote = cluster_votes.get(user)
    cls = (vote or {}).get("classification") or target.get("classification")
    score = (vote or {}).get("score", target.get("score", 0.0))
    label = target.get("label", user)
    base = {"user": user, "coin": coin, "label": label, "score": score,
            "ts": ts}

    if cls == "fade":
        return [{**base, "action": "skip", "reason": "fade_target",
                 "shadow": True}]
    thr = cfg["scorer"]["mirror_score_threshold"]
    if cls != "copy" or score < thr:
        return [{**base, "action": "skip",
                 "reason": f"below_mirror_threshold({score:.1f}<{thr})",
                 "shadow": True}]

    if coin not in cfg["mirror"]["coin_whitelist"]:
        return [{**base, "action": "skip", "reason": "coin_not_whitelisted",
                 "shadow": True}]

    if direction.startswith("Open"):
        notional = sz * px * cfg["mirror"]["multiplier"]
        ok, why = risk_ok(coin, notional)
        if not ok:
            return [{**base, "action": "skip", "reason": f"risk:{why}",
                     "shadow": True}]
        size, breakdown = sizer(fill, target)
        if size is None or size <= EPS:
            return [{**base, "action": "skip",
                     "reason": breakdown.get("decision", "sizer_reject"),
                     "shadow": True, "kelly": breakdown}]
        return [{**base, "action": "open",
                 "side": "long" if "Long" in direction else "short",
                 "size": size, "ref_px": px,
                 "kelly": breakdown,
                 "slippage_buffer_pct":
                     cfg["mirror"]["slippage_buffer_pct"]}]
    if direction.startswith("Close"):
        start = abs(float(fill.get("startPosition", 0) or 0))
        pct = 1.0 if start <= EPS else min(sz / start, 1.0)
        return [{**base, "action": "close", "pct": round(pct, 4),
                 "reason": "target_exit"}]
    return [{**base, "action": "skip", "reason": f"unknown_dir:{direction}"}]


# --------------------------------------------------------------------------
# Live executor (stubbed on purpose)
# --------------------------------------------------------------------------

class LiveExecutor:
    """Order placement. Unwired by design until the exchange API is
    verified: EIP-712 action construction, nonce discipline, and the
    approveAgent API-wallet flow all need a live testnet pass first."""

    def __init__(self, cfg: dict):
        self.cfg = cfg

    def place_ioc(self, coin: str, side: str, size: float,
                  ref_px: float) -> dict:
        raise NotImplementedError(
            "live execution not wired: verify EIP-712 exchange actions and "
            "the approveAgent API-wallet flow on testnet first "
            "(see hyperliquid/README.md, Deployment)")

    def sync_leverage(self, coin: str, target_leverage: int) -> dict:
        raise NotImplementedError(
            "leverage sync not wired: same verification gate as orders")


# --------------------------------------------------------------------------
# WebSocket loop
# --------------------------------------------------------------------------

def run_ws(cfg: dict, targets: dict, on_fill, on_tick=None) -> None:
    """Subscribe userFills per target; dispatch fills to on_fill.

    Per-coin serial queues: each coin gets one worker thread so fills
    for the same coin can never race each other. Each worker owns an
    IntentAggregator: fragmented fills for the coin are grouped into
    intents and deduped by fill hash before reaching on_fill.
    Reconnects with backoff. Requires `websocket-client`.
    """
    try:
        import websocket
    except ImportError:
        log("websocket-client not installed; see requirements.txt. "
            "Paper mode (paper.py) does not need it.")
        sys.exit(3)

    h = cfg["hyperliquid"]
    window_s = float(h["mirror"].get("intent_window_s", 5.0))
    users = [u for u, t in targets.items()
             if t.get("classification") == "copy" and not t.get("example")]
    if not users:
        log("no COPY targets to subscribe; refusing to run an empty loop")
        sys.exit(2)

    work: dict[str, "queue.Queue[dict]"] = {}
    aggs: dict[str, IntentAggregator] = {}
    stop = threading.Event()

    def handle_intent(intent: dict) -> None:
        try:
            on_fill(intent)
        except Exception as e:  # never let one intent kill the loop
            log(f"fill handler error on {intent.get('coin')}: {e}")

    def flush_all_aggs() -> None:
        now = time.time()
        for coin, agg in list(aggs.items()):
            for intent in agg.flush_expired(now):
                handle_intent(intent)

    def worker(coin: str, q: "queue.Queue[dict]") -> None:
        agg = aggs.setdefault(coin, IntentAggregator(window_s))
        while not stop.is_set():
            try:
                fill = q.get(timeout=1.0)
            except queue.Empty:
                continue
            try:
                dup, rolled = agg.add(fill)
                if dup:
                    log(f"duplicate fill dropped for {coin}")
                    continue
                for intent in rolled + agg.flush_expired(time.time()):
                    handle_intent(intent)
            except Exception as e:  # never let one fill kill the loop
                log(f"fill handler error on {coin}: {e}")
            finally:
                q.task_done()

    def dispatch(fill: dict) -> None:
        coin = str(fill.get("coin", ""))
        if coin not in work:
            work[coin] = queue.Queue()
            threading.Thread(target=worker, args=(coin, work[coin]),
                             daemon=True).start()
        work[coin].put(fill)

    backoff = 1.0
    while not stop.is_set():
        try:
            ws = websocket.create_connection(h["ws_url"], timeout=20)
            for u in users:
                ws.send(json.dumps({
                    "method": "subscribe",
                    # TODO-verify: exact subscription payload shape
                    # against a live WS session.
                    "subscription": {"type": "userFills", "user": u}}))
            log(f"subscribed userFills for {len(users)} targets")
            backoff = 1.0
            while not stop.is_set():
                raw = ws.recv()
                if on_tick:
                    on_tick(time.time())
                flush_all_aggs()  # close intents whose window elapsed
                try:
                    msg = json.loads(raw)
                except (json.JSONDecodeError, TypeError):
                    continue
                data = msg.get("data", msg)
                fills = data.get("fills", [data] if "coin" in data else [])
                for f in fills:
                    if isinstance(f, dict) and f.get("coin"):
                        dispatch(f)
        except Exception as e:
            log(f"ws error ({e}); reconnecting in {backoff:.0f}s")
            time.sleep(backoff)
            backoff = min(backoff * 2, 60)
