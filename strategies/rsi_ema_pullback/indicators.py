"""RSI pullback to EMA(50) indicators (classic pullback system).

Setup (Connors/Raschke lineage, *Street Smarts*, 1995):
- Trend: EMA(50). Uptrend is close above a *rising* EMA(50);
  downtrend is close below a *falling* EMA(50).
- RSI(14) (Wilder). In an uptrend the pullback is RSI dipping
  below 40; the entry trigger is RSI crossing back above 40.
  The mirror in a downtrend is RSI rising above 60, then
  crossing back below 60.

The "armed" state lives in the signal layer: a dip arms the
setup, the cross fires it, and the trend filter must still
hold at the cross. A dip that happens while the trend is
broken does not arm anything.

Columns:
    ema50, rsi, ema_rising, ema_falling, trend_up, trend_down,
    rsi_below_40, rsi_above_60, rsi_cross_up_40, rsi_cross_dn_60,
    atr

Seeding: EMA(50) is NaN for the first 49 bars and RSI(14) is
seeded by base.rsi (flat/zero-delta stretches read 0 — see
base.rsi: gains 0 and losses 0 give RSI 0). Trend columns are
False until EMA(50) exists, so no setup can fire before the
EMA is defined. WARMUP = 60 covers the EMA(50) warm-up plus
margin. No lookahead: every value on bar i uses only bars
0..i (crossed_above/below compare bar i with bar i-1).
"""

import pandas as pd

from strategies import base as B

EMA_N = 50
RSI_N = 14
RSI_OVERSOLD = 40.0
RSI_OVERBOUGHT = 60.0
RSI_LONG_EXIT = 70.0
RSI_SHORT_EXIT = 30.0


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]

    ema50 = B.ema(c, EMA_N)
    df["ema50"] = ema50
    df["rsi"] = B.rsi(c, RSI_N)

    ema_prev = ema50.shift(1)
    df["ema_rising"] = (ema50 > ema_prev).fillna(False).astype(bool)
    df["ema_falling"] = (ema50 < ema_prev).fillna(False).astype(bool)
    df["trend_up"] = ((c > ema50) & df["ema_rising"]).fillna(False).astype(bool)
    df["trend_down"] = ((c < ema50) & df["ema_falling"]).fillna(False).astype(bool)

    rsi = df["rsi"]
    df["rsi_below_40"] = (rsi < RSI_OVERSOLD).fillna(False).astype(bool)
    df["rsi_above_60"] = (rsi > RSI_OVERBOUGHT).fillna(False).astype(bool)
    df["rsi_cross_up_40"] = B.crossed_above(rsi, RSI_OVERSOLD).fillna(False).astype(bool)
    df["rsi_cross_dn_60"] = B.crossed_below(rsi, RSI_OVERBOUGHT).fillna(False).astype(bool)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
