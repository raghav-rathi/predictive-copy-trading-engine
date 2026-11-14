"""Dynamic Zones RSI -- Zamansky & Stendahl, Stocks & Commodities July 1996 V15:7.

ORIGINAL percentile construction (not fixed 30/70 levels): the buy and
sell zones are recomputed every bar from the trailing distribution of
RSI itself, so the zones adapt to bull vs bear regimes instead of
requiring the trader to swap fixed levels by market opinion.

    rsi       = RSI(14) of close (Wilder)
    buy_zone  = 12th percentile of RSI over rolling 70 bars
    sell_zone = 88th percentile of RSI over rolling 70 bars

Long when RSI crosses back above the buy zone after dipping below it
(oversold bounce); short when RSI crosses back below the sell zone
after exceeding it. Exits at RSI crossing 50 (momentum back to
neutral) or on a touch of the opposite zone.

Also computed (comparison only, not traded): the common Bollinger
variant -- mean +/- 0.8 sigma of RSI over 20 bars -- recorded in
CALIBRATION.md.

Columns:

    rsi          -- RSI(14)
    buy_zone     -- rolling 70-bar 12th percentile of RSI
    sell_zone    -- rolling 70-bar 88th percentile of RSI
    rsi_bb_mid   -- rolling 20-bar mean of RSI
    rsi_bb_upper -- mid + 0.8 * rolling 20-bar std of RSI
    rsi_bb_lower -- mid - 0.8 * rolling 20-bar std of RSI
    atr          -- Wilder ATR(14) for the risk layer

No lookahead: every rolling window on bar j uses data through bar j
only. The percentile zones need 70 bars to form, hence WARMUP=100.
"""

import numpy as np
import pandas as pd

from strategies import base as B

RSI_LEN = 14    # shipped default (original paper)
ZONE_LEN = 70   # shipped default (original paper: 70-bar sample)
BUY_PCT = 12    # buy zone = 12th percentile ("below 88% of the sample")
SELL_PCT = 88   # sell zone = 88th percentile ("above 88% of the sample")
BB_LEN = 20     # Bollinger-variant window (comparison only)
BB_K = 0.8      # Bollinger-variant band width in sigmas (comparison only)


def add_indicators(df: pd.DataFrame, rsi_n: int = RSI_LEN,
                   zone_n: int = ZONE_LEN,
                   buy_pct: float = BUY_PCT,
                   sell_pct: float = SELL_PCT,
                   bb_n: int = BB_LEN, bb_k: float = BB_K) -> pd.DataFrame:
    df = df.copy()
    rsi = B.rsi(df["c"], rsi_n)
    df["rsi"] = rsi
    df["buy_zone"] = rsi.rolling(zone_n, min_periods=zone_n).quantile(buy_pct / 100.0)
    df["sell_zone"] = rsi.rolling(zone_n, min_periods=zone_n).quantile(sell_pct / 100.0)
    bb_mid = rsi.rolling(bb_n, min_periods=bb_n).mean()
    bb_sd = rsi.rolling(bb_n, min_periods=bb_n).std()
    df["rsi_bb_mid"] = bb_mid
    df["rsi_bb_upper"] = bb_mid + bb_k * bb_sd
    df["rsi_bb_lower"] = bb_mid - bb_k * bb_sd
    df["atr"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
