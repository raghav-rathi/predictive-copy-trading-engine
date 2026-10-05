"""BOT 2 - CARTOGRAPHER.

For each watchlist coin, maps where a short can enter. Never trades, never
sizes.

Method:
  1. Anchor the impulse: anchor_high = highest daily high of the last
     ANCHOR_LOOKBACK_DAYS days ending at C1; current_low = lowest daily low
     from the anchor to now.
  2. Scan 4H candles across the FULL impulse for bearish Fair Value Gaps:
     candle[i].low > candle[i-2].high with a red displacement middle candle
     (range > FVG_MIN_DISPLACEMENT_ATR_MULT * ATR(FVG_ATR_PERIOD)).
     Zone = [candle[i-2].high, candle[i].low].
  3. Build the ladder top-to-bottom; merge overlapping zones.
  4. Zone state: FRESH -> TESTED on a partial wick test (4H high enters the
     zone, 4H close stays below the zone top); INVALID on a 4H close above
     the zone top (zone removed from the ladder).
"""
from dataclasses import dataclass, field

from .config import get


@dataclass
class Zone:
    top: float
    bottom: float
    formed_ms: int
    state: str = "FRESH"  # FRESH | TESTED


@dataclass
class Ladder:
    coin: str
    asof_ms: int
    anchor_high: float
    anchor_ms: int
    current_low: float
    zones: list = field(default_factory=list)  # top-to-bottom

    def best_fresh(self):
        for z in self.zones:
            if z.state == "FRESH":
                return z
        return None

    def best(self):
        return self.zones[0] if self.zones else None


def _atr(candles, period):
    if len(candles) < period + 1:
        return None
    trs = []
    for i in range(1, period + 1):
        c, p = candles[-i], candles[-i - 1]
        trs.append(max(c["h"] - c["l"], abs(c["h"] - p["c"]),
                       abs(c["l"] - p["c"])))
    return sum(trs) / len(trs)


def _find_fvgs(h4):
    """Raw BEARISH FVG zones from 4H candles (oldest->newest).

    Bearish FVG (supply zone, for shorts): the middle candle displaces DOWN
    so hard it leaves a gap above - candle[i-2].low > candle[i].high.
    Zone = [candle[i].high, candle[i-2].low].
    """
    period = get("FVG_ATR_PERIOD")
    mult = get("FVG_MIN_DISPLACEMENT_ATR_MULT")
    zones = []
    for i in range(2, len(h4)):
        prev2, mid, cur = h4[i - 2], h4[i - 1], h4[i]
        if prev2["l"] <= cur["h"]:
            continue  # no bearish gap
        atr = _atr(h4[:i], period)
        if atr is None:
            continue
        if not (mid["c"] < mid["o"]):
            continue  # displacement candle must be red
        if (mid["h"] - mid["l"]) < mult * atr:
            continue
        zones.append(Zone(top=prev2["l"], bottom=cur["h"],
                          formed_ms=cur["t"]))
    return zones


def _merge(zones):
    """Merge overlapping zones, keep top-to-bottom order."""
    zones = sorted(zones, key=lambda z: z.top, reverse=True)
    merged = []
    for z in zones:
        if merged and z.top > merged[-1].bottom:
            m = merged[-1]
            m.top = max(m.top, z.top)
            m.bottom = min(m.bottom, z.bottom)
            m.formed_ms = min(m.formed_ms, z.formed_ms)
        else:
            merged.append(z)
    return merged


def build_ladder(coin, daily, h4, asof_ms):
    """Build the FVG ladder as of `asof_ms`.

    `daily`: daily candles oldest->newest, ending at/before asof.
    `h4`:    4H candles oldest->newest, ending at/before asof.
    """
    lookback = get("ANCHOR_LOOKBACK_DAYS")
    window = [c for c in daily if c["t"] <= asof_ms][-lookback:]
    if not window:
        return None
    anchor = max(window, key=lambda c: c["h"])
    anchor_high, anchor_ms = anchor["h"], anchor["t"]
    tail = [c for c in daily if anchor_ms <= c["t"] <= asof_ms]
    if not tail:
        return None
    current_low = min(c["l"] for c in tail)

    impulse_h4 = [c for c in h4 if anchor_ms <= c["t"] <= asof_ms]
    zones = [z for z in _merge(_find_fvgs(impulse_h4))
             if z.bottom > current_low and z.top < anchor_high]

    # State: scan 4H candles after each zone formed.
    by_time = sorted(impulse_h4, key=lambda c: c["t"])
    live = []
    for z in zones:
        after = [c for c in by_time if c["t"] > z.formed_ms]
        invalid = any(c["c"] > z.top for c in after)
        if invalid:
            continue  # 4H close above zone top -> zone dead
        tested = any(c["h"] > z.bottom and c["c"] < z.top for c in after)
        z.state = "TESTED" if tested else "FRESH"
        live.append(z)
    live.sort(key=lambda z: z.top, reverse=True)
    return Ladder(coin=coin, asof_ms=asof_ms, anchor_high=anchor_high,
                  anchor_ms=anchor_ms, current_low=current_low, zones=live)
