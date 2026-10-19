"""Fibonacci pullback-entry indicators.

Trend filter: SMA200 of close.
Swing frame: trailing ``swing_window``-bar highest high (swingH) and
lowest low (swingL) -- the last completed impulse leg.

Long pocket (uptrend impulse swingL -> swingH):
    lretr50  = swingH - 0.50  * (swingH - swingL)
    lretr618 = swingH - 0.618 * (swingH - swingL)
    lretr786 = swingH - 0.786 * (swingH - swingL)
Entry when the bar's low dips to/below the 50% retracement, holds above
the 78.6% level, and closes back above 61.8% (reclaim).

Short pocket (downtrend leg swingH -> swingL), mirrored:
    sretr382 = swingL + 0.382 * (swingH - swingL)
    sretr50  = swingL + 0.50  * (swingH - swingL)
    sretr618 = swingL + 0.618 * (swingH - swingL)
Entry when the bar's high pushes into the 38.2-50% retracement zone,
holds below 61.8%, and closes back below 38.2%.

No lookahead: every value on bar i uses bars through i only.

Source: https://www.financialtechwiz.com/post/fibonacci-retracement-tradingview/
"""

import pandas as pd

from strategies import base as B

SWING_WINDOW = 60
SMA_N = 200


def add_indicators(
    df: pd.DataFrame,
    swing_window: int = SWING_WINDOW,
    sma_n: int = SMA_N,
) -> pd.DataFrame:
    df = df.copy()
    c, h, l = df["c"], df["h"], df["l"]
    df["sma200"] = B.sma(c, sma_n)
    swingH = h.rolling(swing_window, min_periods=swing_window).max()
    swingL = l.rolling(swing_window, min_periods=swing_window).min()
    df["swingH"] = swingH
    df["swingL"] = swingL
    rng = swingH - swingL
    df["lretr50"] = swingH - 0.50 * rng
    df["lretr618"] = swingH - 0.618 * rng
    df["lretr786"] = swingH - 0.786 * rng
    df["sretr382"] = swingL + 0.382 * rng
    df["sretr50"] = swingL + 0.50 * rng
    df["sretr618"] = swingL + 0.618 * rng
    # zone flags: price inside the pullback pocket on this bar
    df["in_zone_long"] = (l <= df["lretr50"]) & (l > df["lretr786"]) & (c > df["lretr618"])
    df["in_zone_short"] = (h >= df["sretr382"]) & (h < df["sretr618"]) & (c < df["sretr382"])
    df["atr"] = B.atr(h, l, c, 14)
    return df
