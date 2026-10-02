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
    for the same coin can never race each other. Reconnects with
    backoff. Requires `websocket-client`.
    """
    try:
        import websocket
    except ImportError:
        log("websocket-client not installed; see requirements.txt. "
            "Paper mode (paper.py) does not need it.")
        sys.exit(3)

    h = cfg["hyperliquid"]
    users = [u for u, t in targets.items()
             if t.get("classification") == "copy" and not t.get("example")]
    if not users:
        log("no COPY targets to subscribe; refusing to run an empty loop")
        sys.exit(2)

    work: dict[str, "queue.Queue[dict]"] = {}
    stop = threading.Event()

    def worker(coin: str, q: "queue.Queue[dict]") -> None:
        while not stop.is_set():
            try:
                fill = q.get(timeout=1.0)
            except queue.Empty:
                continue
            try:
                on_fill(fill)
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
