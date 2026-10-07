#!/usr/bin/env python3
"""Uncopyable-flow filter for the Hyperliquid copy engine.

Thesis (from open-source copy-trading research — lindagrey's
hyperliquid-copy-trader wallet heuristics and tradingstrategy-ai's HFT
identification metrics): the wallets a copier must NEVER mirror are

  * HFT / high-frequency traders — dozens of fills per hour; a polling
    copier cannot keep up and bleeds on latency/slippage,
  * scalpers — average hold under ~5 minutes; fills won't land in time,
  * market makers — hold long AND short on the same coin simultaneously;
    mirroring both sides is a guaranteed loss,
  * chronic flippers — constantly reverse direction on the same coin;
    the copy arrives after the edge is gone.

These are detected from the wallet's own fills (no extra API calls):
`userFillsByTime` rows with dir/coin/sz/px/time. A flagged wallet is
forced to "pass" (never copy, never fade) regardless of its PnL score —
fading an HFT book has the same latency problem in reverse.

Thresholds live in the `flow_filter` config section; defaults are
conservative (flag only clear-cut cases) so the filter rarely fires on
ordinary swing-trader flow.

Stdlib only.
"""
from __future__ import annotations

from collections import defaultdict


def _fill_ts_s(f: dict) -> float:
    """Fill timestamp in seconds (Hyperliquid uses ms epoch; fixtures
    sometimes use seconds)."""
    ts = float(f.get("time", f.get("ts", 0)) or 0)
    if ts > 1e12:
        ts /= 1000.0
    return ts


def _dir(fill: dict) -> str:
    return str(fill.get("dir", ""))


def _is_open(fill: dict) -> bool:
    return _dir(fill).startswith("Open")


def _side(fill: dict) -> int:
    return 1 if "Long" in _dir(fill) else -1


def dedup_fills(fills: list[dict]) -> list[dict]:
    """Aggregate fill fragments into parent orders.

    One market order sweeping the book prints many fill records at the
    same millisecond (up to 22 observed on a single vault). Counting
    fragments as trades wildly overstates activity — group by
    (timestamp, coin, dir), summing size and volume-weighting price.
    """
    groups: dict[tuple, dict] = {}
    for f in fills:
        coin = str(f.get("coin", ""))
        sz = float(f.get("sz", 0) or 0)
        px = float(f.get("px", 0) or 0)
        if not coin or sz <= 0 or px <= 0:
            continue
        key = (int(_fill_ts_s(f) * 1000), coin, _dir(f))
        g = groups.get(key)
        if g is None:
            groups[key] = {"coin": coin, "dir": _dir(f),
                           "time": f.get("time", f.get("ts", 0)),
                           "sz": sz, "px": px,
                           "closedPnl": f.get("closedPnl", f.get("pnl")),
                           "n_fragments": 1}
        else:
            total_sz = g["sz"] + sz
            g["px"] = (g["px"] * g["sz"] + px * sz) / total_sz
            g["sz"] = total_sz
            g["n_fragments"] += 1
    return list(groups.values())


def flow_metrics(fills: list[dict], burst_per_hour: int = 100) -> dict:
    """Compute copyability metrics from raw fills.

    Returns dict with:
      n_fills, span_hours, trades_per_hour,
      avg_hold_s (open->close pairing per coin, FIFO),
      flip_count (direction reversals on the same coin),
      both_sides_coins (coins with overlapping open long+short),
      burst_hours_100ph (distinct hours with >= burst_per_hour orders)
    """
    fills = dedup_fills(fills)  # count parent orders, not fragments
    m: dict = {"n_fills": len(fills), "span_hours": 0.0,
               "trades_per_hour": 0.0, "avg_hold_s": float("inf"),
               "flip_count": 0, "both_sides_coins": [],
               "max_trades_in_any_hour": 0}
    if not fills:
        return m

    by_ts = sorted(fills, key=_fill_ts_s)
    t0, t1 = _fill_ts_s(by_ts[0]), _fill_ts_s(by_ts[-1])
    span_h = max((t1 - t0) / 3600.0, 1.0 / 3600.0)
    m["span_hours"] = round(span_h, 2)
    m["trades_per_hour"] = round(len(by_ts) / span_h, 2)

    # burstiness: distinct sliding 3600s windows with >= burst_threshold
    # parent orders. A single busy hour is a rebalance, not a structure;
    # the flag needs recurring machine flow.
    tstamps = sorted(_fill_ts_s(f) for f in by_ts)
    burst_hours: set[int] = set()
    j = 0
    for i in range(len(tstamps)):
        while tstamps[i] - tstamps[j] >= 3600:
            j += 1
        if i - j + 1 >= burst_per_hour:
            burst_hours.add(int(tstamps[i] // 3600))
    m["burst_hours_100ph"] = len(burst_hours)

    # FIFO open->close pairing per coin for hold times + flip detection
    # + simultaneous both-sides detection.
    holds: list[float] = []
    flips = 0
    both_sides: set[str] = set()
    open_lots: dict[str, list[dict]] = defaultdict(list)
    last_dir: dict[str, int] = {}
    for f in by_ts:
        coin = str(f.get("coin", ""))
        ts = _fill_ts_s(f)
        side = _side(f)
        if _is_open(f):
            # both-sides: an open long while a short lot is still open
            # on the same coin (or vice versa) = market-maker signature.
            if any(lot["side"] != side for lot in open_lots[coin]):
                both_sides.add(coin)
            open_lots[coin].append({"side": side, "ts": ts,
                                    "sz": float(f.get("sz", 0))})
            if coin in last_dir and last_dir[coin] != side:
                flips += 1
            last_dir[coin] = side
        else:
            # match closes FIFO to measure hold time
            remaining = float(f.get("sz", 0))
            while remaining > 1e-12 and open_lots[coin]:
                lot = open_lots[coin][0]
                take = min(remaining, lot["sz"])
                holds.append(ts - lot["ts"])
                lot["sz"] -= take
                remaining -= take
                if lot["sz"] <= 1e-12:
                    open_lots[coin].pop(0)
    if holds:
        m["avg_hold_s"] = round(sum(holds) / len(holds), 1)
    m["flip_count"] = flips
    m["both_sides_coins"] = sorted(both_sides)
    return m


# Thresholds are derived from the copier's own constraints, not tuned
# to the data:
#  - scalper_max_hold_s = our 30-min poll interval: flow that turns over
#    faster than we poll decays before the copy lands.
#  - hft_trades_per_hour = 30 parent orders/hr sustained: at that rate
#    per-trade signal is below fee/latency noise for a polling copier.
#  - hft_burst_per_hour = 100 parent orders in a sliding hour: genuine
#    machine flow (counts parent orders AFTER fragment dedup).
DEFAULT_FLOW_CONFIG = {
    "hft_trades_per_hour": 30.0,   # sustained parent-order rate -> HFT
    "hft_burst_per_hour": 100,     # single sliding-hour burst -> HFT
    "hft_min_fills": 50,           # need a real sample before flagging
    "scalper_max_hold_s": 1800,    # avg hold under our poll interval
    "scalper_min_closes": 50,
    "flipper_min_ratio": 0.5,      # flips / closes above this -> flipper
    "flipper_min_closes": 30,
}


def detect_uncopyable(metrics: dict, n_closes: int,
                      cfg: dict | None = None) -> list[str]:
    """Return list of uncopyable-flow flags (empty = copyable flow).

    Flags: "hft", "scalper", "market_maker", "flipper".
    """
    cfg = cfg or DEFAULT_FLOW_CONFIG
    flags: list[str] = []
    n = metrics.get("n_fills", 0)
    # Sustained rate needs a real sample; recurring burst-hours (>=3 in
    # the window) indicate structural machine flow, while one or two
    # busy hours are just rebalances.
    if metrics.get("burst_hours_100ph", 0) >= 3:
        flags.append("hft")
    elif (n >= cfg["hft_min_fills"]
            and metrics.get("trades_per_hour", 0) >= cfg["hft_trades_per_hour"]):
        flags.append("hft")
    if n_closes >= cfg["scalper_min_closes"]:
        if metrics.get("avg_hold_s", float("inf")) <= cfg["scalper_max_hold_s"]:
            flags.append("scalper")
    if metrics.get("both_sides_coins"):
        flags.append("market_maker")
    if n_closes >= cfg["flipper_min_closes"]:
        ratio = metrics.get("flip_count", 0) / max(n_closes, 1)
        if ratio >= cfg["flipper_min_ratio"]:
            flags.append("flipper")
    return flags


def is_uncopyable(fills: list[dict], n_closes: int,
                  cfg: dict | None = None) -> tuple[list[str], dict]:
    """Convenience: (flags, metrics) for a wallet's fills."""
    cfg = cfg or DEFAULT_FLOW_CONFIG
    metrics = flow_metrics(fills,
                           burst_per_hour=cfg.get("hft_burst_per_hour", 100))
    return detect_uncopyable(metrics, n_closes, cfg), metrics
