#!/usr/bin/env python3
"""Robinhood Chain sequencer feed client + trigger/fill correlator.

Robinhood Chain is an Arbitrum-Orbit L2 with ~100ms blocks and a single
sequencer, which publishes a near-real-time feed of pending block data at
wss://feed.mainnet.chain.robinhood.com (Arbitrum feed protocol: JSON
messages carrying `sequenceNumber` and the L2 block payload once relayed).

Role in the pipeline: the Solana watcher (solana_watcher.py) says "wallet
X will probably receive a fill within ~0.5-1.6s". This client watches the
feed so the engine can learn, after the fact and later in real time:
  * which block the fill actually landed in,
  * the trigger->fill latency distribution (is the 5-16 block window real
    on this chain, this week?),
  * when a trigger's window has expired without a fill (kill the burst).

Honesty note: the exact message schema of Robinhood's feed deployment and
whether it carries pre-confirmation sequencer data (vs post-batch L1-
relayed messages only) is TODO-verify-on-chain. The parser below accepts
both Arbitrum feed message shapes defensively and records raw fields it
does not understand rather than assuming. Nothing here signs or sends.

Correlation logic is deliberately stub-shaped: matching a trigger to a
fill requires knowing which token the whale bought, which the feed alone
cannot tell us (same problem the detector contract solves on-chain).
Until fills are attributed (via Blockscout traces, scorer-side), the
correlator matches on recipient wallet + time window only and labels its
output `candidate`, never `confirmed`.

Stdlib only; reuses the minimal websocket from solana_watcher.
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import sys
import time
from collections import deque
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from solana_watcher import WebSocket, WSClosed  # noqa: E402

FEED_URL = "wss://feed.mainnet.chain.robinhood.com"
BLOCK_TIME_S = 0.1            # ~100ms blocks (chain docs; re-measure below)
EXPECTED_FILL_WINDOW_S = (0.3, 2.5)   # research said 0.5-1.6s; pad both sides


class FeedStats:
    """Running block-cadence measurement; do not trust the nominal 100ms."""

    def __init__(self) -> None:
        self.last_block: int | None = None
        self.last_ts: float | None = None
        self.intervals: deque[float] = deque(maxlen=500)

    def observe(self, block: int, ts: float) -> float | None:
        if self.last_block is not None and block > self.last_block:
            dt = (ts - self.last_ts) / (block - self.last_block)
            self.intervals.append(dt)
            self.last_block, self.last_ts = block, ts
            return dt
        if self.last_block is None:
            self.last_block, self.last_ts = block, ts
        return None

    def median_block_time(self) -> float | None:
        if not self.intervals:
            return None
        s = sorted(self.intervals)
        return s[len(s) // 2]


def parse_feed_message(msg: dict) -> dict | None:
    """Extract {block, timestamp, recipients[]} from an Arbitrum-style
    feed message. Returns None for heartbeats/acks.

    Two shapes are handled:
      A) {"sequenceNumber": n, "message": {"header": {...}, "l2Msg": ...}}
         -- sequencer feed; block number may only appear after relay.
      B) relayed broadcasts carrying an explicit block header with
         number/timestamp fields.
    `recipients` is best-effort: top-level tx `to` addresses if the payload
    inlines transactions, else empty. Feed payloads may omit tx bodies
    entirely; correlate() tolerates that (window-level stats only).
    """
    if not isinstance(msg, dict):
        return None
    payload = msg.get("message") or msg
    header = payload.get("header") or payload.get("blockHeader") or {}
    block = header.get("blockNumber") or header.get("number") \
        or payload.get("blockNumber")
    ts = header.get("timestamp") or payload.get("timestamp")
    if block is None:
        return None
    recipients: list[str] = []
    txs = payload.get("transactions") or payload.get("txs") or []
    for tx in txs:
        if isinstance(tx, dict):
            to = tx.get("to") or tx.get("destination")
            if to:
                recipients.append(str(to).lower())
    return {"block": int(block), "timestamp": ts,
            "recipients": recipients, "raw_keys": sorted(payload.keys())}


class Correlator:
    """Matches pending deposit triggers to later blocks.

    A trigger is resolved as:
      candidate -- whale address appears as a tx recipient inside the
                   expected window (necessary, not sufficient: any token);
      expired   -- window closed with no appearance.
    Confirmed attribution stays TODO until token-level trace data (the
    same balance-diff the detector contract performs) is wired in.
    """

    def __init__(self, window: tuple[float, float] = EXPECTED_FILL_WINDOW_S):
        self.window = window
        self.pending: list[dict] = []
        self.resolved: list[dict] = []

    def add_trigger(self, whale: str, ts: float) -> None:
        if whale:
            self.pending.append({"whale": whale.lower(), "ts": ts})

    def observe_block(self, block: int, ts: float, recipients: list[str]) -> None:
        recips = set(recipients)
        still: list[dict] = []
        for trig in self.pending:
            dt = ts - trig["ts"]
            if trig["whale"] in recips and self.window[0] <= dt <= self.window[1]:
                self.resolved.append({**trig, "block": block, "latency_s": dt,
                                      "status": "candidate"})
            elif dt > self.window[1]:
                self.resolved.append({**trig, "block": None, "latency_s": dt,
                                      "status": "expired"})
            else:
                still.append(trig)
        self.pending = still

    def drain_resolved(self) -> list[dict]:
        out, self.resolved = self.resolved, []
        return out


def run(cfg: dict) -> int:
    url = cfg.get("robinhood", {}).get("feed_url", FEED_URL)
    stats, corr = FeedStats(), Correlator()
    # Triggers arrive on stdin as NDJSON (same bus as the engine's), so:
    #   solana_watcher.py | tee triggers.ndjson | chain_feed.py
    # Non-blocking stdin polling inside the feed loop is awkward stdlib-only;
    # for the scaffold the correlator is exercised via --replay instead.
    attempt = 0
    while True:
        try:
            ws = WebSocket(url)
            attempt = 0
            print(f"connected to sequencer feed {url}", file=sys.stderr)
            while True:
                msg = json.loads(ws.recv_text())
                parsed = parse_feed_message(msg)
                if parsed is None:
                    continue
                dt = stats.observe(parsed["block"], time.time())
                corr.observe_block(parsed["block"], time.time(),
                                   parsed["recipients"])
                for r in corr.drain_resolved():
                    print(json.dumps({"type": "fill_correlation", **r}))
                if dt is not None and stats.last_block % 600 == 0:
                    print(f"block {stats.last_block} median block time "
                          f"{stats.median_block_time()}s", file=sys.stderr)
        except (WSClosed, OSError, ValueError) as e:
            attempt += 1
            backoff = min(2 ** attempt, 60)
            print(f"feed dropped ({e}); reconnect in {backoff}s", file=sys.stderr)
            if attempt > 10:
                return 3
            time.sleep(backoff)


def replay(path: str) -> int:
    """Offline self-check: feed a captured NDJSON of feed messages +
    trigger lines through the parser/correlator. Used until the live
    schema is verified; keeps the correlation math honest and testable."""
    stats, corr = FeedStats(), Correlator()
    n_blocks = n_corr = 0
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            if obj.get("type") == "fomo_deposit" and obj.get("whale"):
                corr.add_trigger(obj["whale"], obj.get("sol_timestamp", 0))
                continue
            parsed = parse_feed_message(obj)
            if parsed:
                n_blocks += 1
                ts = parsed["timestamp"] or time.time()
                stats.observe(parsed["block"], ts)
                corr.observe_block(parsed["block"], ts, parsed["recipients"])
                for _ in corr.drain_resolved():
                    n_corr += 1
    print(f"replayed {n_blocks} blocks, {n_corr} correlations, "
          f"median block time {stats.median_block_time()}s")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", default=None)
    ap.add_argument("--replay", default=None,
                    help="offline-check a captured NDJSON instead of live feed")
    args = ap.parse_args()
    signal.signal(signal.SIGINT, lambda *_: sys.exit(0))
    if args.replay:
        return replay(args.replay)
    cfg = {}
    if args.config:
        with open(args.config) as f:
            cfg = json.load(f)
    return run(cfg)


if __name__ == "__main__":
    sys.exit(main())
