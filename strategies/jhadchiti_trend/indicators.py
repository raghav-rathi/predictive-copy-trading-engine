"""jhadchiti trend-following indicators (mechanism from github.com/jhadchiti
crypto-trading-system Strategy 1, marked LIVE by its author — summarized in
our own words, adapted to 1h bars).

Requires 'btc_c' (BTC 1h closes aligned by timestamp) and 'fund_ok'
(hourly |funding| <= 0.00025) columns pre-attached by the backtest script
(prep_jhadchiti.attach_jhadchiti_inputs); raises a clear error otherwise so
the network-free unit tests stay honest.

Indicators:
  * 55-period close channel (breakout level), 20-period close channel (exit)
  * BTC SMA(200) rising vs 20 bars ago — 1h adaptation of the author's
    daily-frame BTC-regime rule, documented here
  * 30-period returns of the coin and of BTC — adaptation of the author's
    top-20%-vs-BTC universe filter to our 3-coin universe
  * ATR(20) for the 2x stop
"""

import pandas as pd

from strategies import base as B

CHAN_N = 55
EXIT_CHAN_N = 20
REGIME_SMA_N = 200
REGIME_LOOKBACK = 20
MOM_N = 30
ATR_N = 20


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    for col in ("btc_c", "fund_ok"):
        if col not in df.columns:
            raise ValueError(
                f"jhadchiti_trend.add_indicators needs '{col}' pre-attached "
                "(see _scratch/prep_jhadchiti.attach_jhadchiti_inputs)"
            )
    df = df.copy()
    df["chan55_hi"] = df["c"].shift(1).rolling(CHAN_N, min_periods=CHAN_N).max()
    df["chan55_lo"] = df["c"].shift(1).rolling(CHAN_N, min_periods=CHAN_N).min()
    df["chan20_hi"] = df["c"].shift(1).rolling(EXIT_CHAN_N, min_periods=EXIT_CHAN_N).max()
    df["chan20_lo"] = df["c"].shift(1).rolling(EXIT_CHAN_N, min_periods=EXIT_CHAN_N).min()
    sma200 = B.sma(df["btc_c"], REGIME_SMA_N)
    df["btc_regime_up"] = sma200 > sma200.shift(REGIME_LOOKBACK)
    df["ret30"] = df["c"] / df["c"].shift(MOM_N) - 1
    df["btc_ret30"] = df["btc_c"] / df["btc_c"].shift(MOM_N) - 1
    df["atr20"] = B.atr(df["h"], df["l"], df["c"], ATR_N)
    return df
