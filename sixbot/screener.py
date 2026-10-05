"""BOT 1 - SCREENER.

Watches daily closes and emits flip events. Short-only desk:
bearish flips are tradeable, bullish flips are context only.

Bearish flip (C1, C2, C3 = three consecutive CLOSED daily candles):
  - C1 closes down                    (C1.close < C1.open)
  - C2 closes below C1's close        (C2.close < C1.close)
    and does not take out C1's high   (C2.high < C1.high, strict: no touch)
  - C3 body closes below C2's close  (C3.close < C2.close)
    and does not touch C1's high      (C3.high < C1.high)
  - Dojis are valid. C2 does not need to be red.

PRIME tag: daily flipped down while the 4H is bouncing
(latest closed 4H candle green and price above the recent 4H low).
"""
from dataclasses import dataclass

from .config import get


@dataclass
class FlipEvent:
    coin: str
    date: str          # YYYY-MM-DD of C3's close
    timestamp_ms: int  # C3 close time
    direction: str     # "bear" (tradeable) | "bull" (context only)
    prime: bool        # bearish flip + 4H bouncing


def detect_flip(daily):
    """Return (direction, c1, c2, c3) for the last three CLOSED daily candles,
    or None. `daily` is oldest->newest; the caller must exclude the live candle.
    """
    if len(daily) < 3:
        return None
    c1, c2, c3 = daily[-3], daily[-2], daily[-1]

    bear = (
        c1["c"] < c1["o"]
        and c2["c"] < c1["c"] and c2["h"] < c1["h"]
        and c3["c"] < c2["c"] and c3["h"] < c1["h"]
    )
    if bear:
        return ("bear", c1, c2, c3)
    bull = (
        c1["c"] > c1["o"]
        and c2["c"] > c1["c"] and c2["l"] > c1["l"]
        and c3["c"] > c2["c"] and c3["l"] > c1["l"]
    )
    if bull:
        return ("bull", c1, c2, c3)
    return None


def is_4h_bouncing(h4):
    """PRIME bounce test: latest closed 4H candle green and price above the
    lowest low of the last PRIME_4H_BOUNCE_BARS 4H candles."""
    n = get("PRIME_4H_BOUNCE_BARS")
    if len(h4) < n + 1:
        return False
    window = h4[-(n + 1):-1]  # closed candles only
    last = window[-1]
    if not (last["c"] > last["o"]):
        return False
    return last["c"] > min(c["l"] for c in window)


def scan(daily, h4, coin):
    """Run the screener as of the latest closed daily candle.

    Returns a FlipEvent or None. `daily`/`h4` must end at closed candles.
    """
    hit = detect_flip(daily)
    if hit is None:
        return None
    direction, c1, c2, c3 = hit
    prime = direction == "bear" and is_4h_bouncing(h4)
    import datetime
    date = datetime.datetime.fromtimestamp(
        c3["t"] / 1000, tz=datetime.timezone.utc).strftime("%Y-%m-%d")
    return FlipEvent(coin=coin, date=date, timestamp_ms=c3["t"],
                     direction=direction, prime=prime)
