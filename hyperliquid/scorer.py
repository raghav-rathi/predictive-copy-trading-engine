#!/usr/bin/env python3
"""Realized-PnL profiler for Hyperliquid wallets -> 0-100 score.

Adapted from the repo's Robinhood Chain FIFO profiler
(scorer/wallet_scorer.py). The chain-specific fetch here is implemented
against Hyperliquid's public API (POST /info), which needs no auth:

  userFillsByTime -> fills (dir: "Open Long" | "Open Short" |
                            "Close Long" | "Close Short"; sz, px,
                            startPosition, and usually a realized `pnl`
                            on closes)
  portfolio      -> account value + PnL history (not required; fills
                    suffice for per-trade scoring)

TODO-verify: exact fill field names and the `pnl` semantics on close
fills against a live response before trusting scores at scale. The
parsing below is defensive: when a close fill carries no usable `pnl`,
we fall back to FIFO reconstruction from that wallet's own opens.

Predictive scoring (@slash1sol, CopyGrade): public win-rate
leaderboards mislead — past luck is not future edge. The score leans
on forward-looking structure:

  * time-weighted win rate / profit factor: recent closes count more
    (exponential decay, 90d tau); a wallet whose edge died months ago
    does not ride old wins into a copy slot
  * consistency: win-rate distribution across time windows — a 60%
    winner that was 90% then 30% is decaying, not steady
  * minimum-sample guard: wallets with fewer than min_closed_trades
    closed trades are marked "unscored" (score 0.0, classification
    "pass") and can NEVER be copied, however lucky the sample

Scoring (weights from config, default sum 100):
  win_rate        25 pts: 25 * min(weighted_win_rate / 0.6, 1)
  profit_factor   20 pts: 20 * min(weighted_pf / 2.0, 1)
  consistency     15 pts: 15 * (1 - 2*stdev(window win rates))
  max_drawdown    15 pts: 15 * max(0, 1 - dd / 0.5), dd from realized equity
  sample_size     15 pts: 15 * min(closed / 30, 1)
  recency         10 pts: 10 * min(closes_last_30d / 10, 1)

Classification:
  closed < min_closed_trades        -> "pass" (unscored: never copy)
  score >= mirror_score_threshold   -> "copy"
  score <= fade_score_threshold     -> "fade"
  else                              -> "pass" (watch=True when score >= 50)

Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict, deque
from datetime import datetime, timezone

DAY_S = 86400


# --------------------------------------------------------------------------
# Hyperliquid public info API
# --------------------------------------------------------------------------

class HyperliquidInfo:
    """Minimal client for the public /info endpoint (no auth needed)."""

    def __init__(self, info_url: str, pace_s: float = 1.0,
                 max_retries: int = 5):
        self.info_url = info_url
        self.pace_s = pace_s
        self.max_retries = max_retries
        self._last_call = 0.0

    def _post(self, payload: dict):
        data = json.dumps(payload).encode()
        last_err: Exception | None = None
        for attempt in range(self.max_retries):
            wait = self.pace_s - (time.time() - self._last_call)
            if wait > 0:
                time.sleep(wait)
            req = urllib.request.Request(
                self.info_url, data=data,
                headers={"Content-Type": "application/json",
                         "User-Agent": "predictive-copy-trading-engine/0.1"})
            try:
                self._last_call = time.time()
                with urllib.request.urlopen(req, timeout=30) as r:
                    return json.load(r.read().decode())
            except urllib.error.HTTPError as e:
                last_err = e
                if e.code == 429:
                    time.sleep(min(2 ** attempt * 2, 30))
                    continue
                raise
            except (urllib.error.URLError, TimeoutError) as e:
                last_err = e
                time.sleep(min(2 ** attempt, 15))
        raise RuntimeError(f"hyperliquid /info failed {payload.get('type')}: "
                           f"{last_err}")

    def user_fills_by_time(self, address: str, start_ms: int = 0,
                           end_ms: int | None = None) -> list:
        """All fills for a user since start_ms (ms epoch)."""
        payload = {"type": "userFillsByTime", "user": address,
                   "startTime": start_ms}
        if end_ms is not None:
            payload["endTime"] = end_ms
        out = self._post(payload)
        return out if isinstance(out, list) else []

    def clearinghouse_state(self, address: str) -> dict:
        """Positions/margin/account value for a user (defensively parsed)."""
        return self._post({"type": "clearinghouseState", "user": address})


# --------------------------------------------------------------------------
# FIFO profiler
# --------------------------------------------------------------------------

def _fill_dir(fill: dict) -> str:
    return str(fill.get("dir", ""))


def _is_open(fill: dict) -> bool:
    return _fill_dir(fill).startswith("Open")


def _is_close(fill: dict) -> bool:
    return _fill_dir(fill).startswith("Close")


def _fill_side_sign(fill: dict) -> int:
    d = _fill_dir(fill)
    return 1 if "Long" in d else -1


def realized_closes(fills: list[dict], fee_rate: float = 0.0) -> list[dict]:
    """Pair closes to opens FIFO per coin -> realized closes.

    Uses the fill's own `pnl` (Hyperliquid reports realized PnL on close
    fills) when present and numeric; otherwise reconstructs from FIFO
    lots. Each close dict: {coin, ts, pnl_usd, hold_s, sz}.
    """
    lots: dict[str, deque] = defaultdict(deque)
    closes: list[dict] = []
    for f in sorted(fills, key=lambda x: float(x.get("time", x.get("ts", 0)) or 0)):
        coin = str(f.get("coin", ""))
        ts = float(f.get("time", f.get("ts", 0)) or 0)
        sz = abs(float(f.get("sz", 0) or 0))
        px = float(f.get("px", 0) or 0)
        if not coin or sz <= 0 or px <= 0:
            continue
        if _is_open(f):
            lots[coin].append({"side": _fill_side_sign(f), "sz": sz,
                              "px": px, "ts": ts})
        elif _is_close(f):
            side = _fill_side_sign(f)
            remaining = sz
            realized = 0.0
            hold_w = 0.0
            pnl_field = f.get("pnl")
            while remaining > 1e-12 and lots[coin]:
                lot = lots[coin][0]
                take = min(remaining, lot["sz"])
                realized += (px - lot["px"]) * take * lot["side"]
                hold_w += (ts - lot["ts"]) * take
                lot["sz"] -= take
                remaining -= take
                if lot["sz"] <= 1e-12:
                    lots[coin].popleft()
            fee = fee_rate * sz * px
            fifo_pnl = realized - fee
            if isinstance(pnl_field, (int, float)):
                pnl = float(pnl_field) - fee
            else:
                pnl = fifo_pnl  # fallback; flagged in the record
            closes.append({"coin": coin, "ts": ts, "pnl_usd": pnl,
                           "hold_s": hold_w / sz if sz else 0.0,
                           "sz": sz,
                           "pnl_source": "fill" if isinstance(
                               pnl_field, (int, float)) else "fifo"})
    return closes


def score_wallet(fills: list[dict], weights: dict,
                 now_s: float | None = None,
                 min_closed: int | None = None) -> dict:
    """Score a wallet 0-100 from its fills (predictive metrics).

    If min_closed is given and the wallet has fewer closed trades, it
    is returned unscored (score 0.0, "unscored": True) — it can never
    be copied, however lucky the sample looks.
    """
    now_s = now_s or time.time()
    closes = realized_closes(fills)
    n = len(closes)
    stats: dict = {"closed": n, "total_pnl_usd": 0.0, "win_rate": 0.0,
                   "profit_factor": 0.0, "max_drawdown": 0.0,
                   "avg_hold_s": 0.0, "score": 0.0, "unscored": False}
    if n == 0:
        stats["unscored"] = True
        return stats
    if min_closed is not None and n < min_closed:
        stats["unscored"] = True
        return stats

    # Time-decay weights: recent closes count more (90d tau).
    TAU_S = 90 * DAY_S
    tsw = [math.exp(-(now_s - c["ts"]) / TAU_S) for c in closes]
    pnls = [c["pnl_usd"] for c in closes]
    stats["total_pnl_usd"] = sum(pnls)

    wsum = sum(tsw)
    w_win = sum(w for w, p in zip(tsw, pnls) if p > 0)
    w_gross_w = sum(w * p for w, p in zip(tsw, pnls) if p > 0)
    w_gross_l = sum(w * -p for w, p in zip(tsw, pnls) if p < 0)
    win_rate = w_win / wsum if wsum > 0 else 0.0
    profit_factor = (w_gross_w / w_gross_l) if w_gross_l > 0 else (
        99.0 if w_gross_w > 0 else 0.0)
    stats["win_rate"] = round(win_rate, 4)          # time-weighted
    stats["profit_factor"] = round(profit_factor, 4)  # time-weighted

    # Consistency: win-rate distribution across time windows. Split the
    # observed span into 3 windows; a steady 60% beats a decaying
    # 90%-then-30% with the same average.
    t0, t1 = min(c["ts"] for c in closes), max(c["ts"] for c in closes)
    span = max(t1 - t0, 1.0)
    buckets: list[list[float]] = [[], [], []]
    for c, w in zip(closes, tsw):
        idx = min(int((c["ts"] - t0) / span * 3), 2)
        buckets[idx].append(1.0 if c["pnl_usd"] > 0 else 0.0)
    rates = [sum(b) / len(b) for b in buckets if b]
    if len(rates) >= 2:
        consistency = max(0.0, 1.0 - 2.0 * statistics.pstdev(rates))
    else:
        consistency = 1.0  # no evidence of inconsistency
    stats["consistency"] = round(consistency, 4)
    stats["window_win_rates"] = [round(r, 3) for r in rates]

    # Max drawdown on the realized equity curve (unweighted: capital is
    # what it is).
    peak, dd = 0.0, 0.0
    eq = 0.0
    for p in pnls:
        eq += p
        peak = max(peak, eq)
        if peak > 0:
            dd = max(dd, (peak - eq) / peak)
        elif eq < 0:
            dd = 1.0  # never printed a positive mark: full drawdown
    stats["max_drawdown"] = dd
    stats["avg_hold_s"] = statistics.mean(c["hold_s"] for c in closes)
    recent = sum(1 for c in closes if now_s - c["ts"] <= 30 * DAY_S)

    wr_pts = weights["win_rate"] * min(win_rate / 0.6, 1.0)
    pf_pts = weights["profit_factor"] * min(profit_factor / 2.0, 1.0)
    co_pts = weights["consistency"] * consistency
    dd_pts = weights["max_drawdown"] * max(0.0, 1.0 - dd / 0.5)
    n_pts = weights["sample_size"] * min(n / 30.0, 1.0)
    r_pts = weights["recency"] * min(recent / 10.0, 1.0)
    stats["score"] = round(wr_pts + pf_pts + co_pts + dd_pts + n_pts + r_pts, 2)
    stats["components"] = {
        "win_rate": round(wr_pts, 2), "profit_factor": round(pf_pts, 2),
        "consistency": round(co_pts, 2),
        "max_drawdown": round(dd_pts, 2), "sample_size": round(n_pts, 2),
        "recency": round(r_pts, 2)}
    return stats


def classify(score: float, closed: int, min_closed: int,
             mirror_thr: float, fade_thr: float) -> tuple[str, bool]:
    """-> (classification, watch). Thresholds from config.

    Wallets below min_closed_trades are "pass" regardless of score:
    unscored wallets can never be copied (score_wallet marks them
    "unscored" and pins the score to 0.0).
    """
    if closed < min_closed:
        return "pass", False
    if score >= mirror_thr:
        return "copy", False
    if score <= fade_thr:
        return "fade", False
    return "pass", score >= 50.0


def score_address(address: str, info_url: str, weights: dict,
                  mirror_thr: float, fade_thr: float,
                  min_closed: int) -> dict:
    """Fetch, profile, score and classify one wallet."""
    info = HyperliquidInfo(info_url)
    fills = info.user_fills_by_time(address)
    stats = score_wallet(fills, weights, min_closed=min_closed)
    cls, watch = classify(stats["score"], stats["closed"], min_closed,
                          mirror_thr, fade_thr)
    return {"address": address.lower(), "classification": cls,
            "watch": watch, "score": stats["score"], "stats": stats}


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Score Hyperliquid wallets from public fills.")
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", required=True,
                    help="targets.json to write")
    ap.add_argument("addresses", nargs="+")
    args = ap.parse_args()

    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
    from config import load_config
    cfg = load_config(args.config)["hyperliquid"]
    sc = cfg["scorer"]
    wallets = []
    for addr in args.addresses:
        try:
            w = score_address(addr, cfg["info_url"], sc["weights"],
                              sc["mirror_score_threshold"],
                              sc["fade_score_threshold"],
                              sc["min_closed_trades"])
        except Exception as e:  # network/API failure: keep going, mark pass
            print(f"scoring {addr} failed ({e}); marking pass", file=sys.stderr)
            w = {"address": addr.lower(), "classification": "pass",
                 "watch": False, "score": 0.0,
                 "stats": {"error": str(e)}}
        wallets.append(w)
        print(f"{w['address']} -> {w['classification']} "
              f"score={w['score']} closed={w['stats'].get('closed', 0)}")
    with open(args.out, "w") as f:
        json.dump({"wallets": wallets}, f, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
