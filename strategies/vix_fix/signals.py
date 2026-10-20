"""VIX Fix fear-spike mean-reversion signals.

Long: WVF crosses ABOVE its upper Bollinger band (extreme fear spike) ->
long the next bar. Exit when WVF crosses back BELOW the band midline
(the fear spike has deflated), or the harness's max-hold / stop fires.

Short (inverse leg, less-reliable published variant): iWVF crosses
ABOVE its upper band (extreme greed / blow-off) -> short; exit when
iWVF crosses back below its midline.

Signal columns are boolean, no NaN, no lookahead (execution at
next-bar open is handled by the harness).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    long_entry = (df["wvf"] > df["wvf_bb_upper"]) & (
        df["wvf"].shift(1) <= df["wvf_bb_upper"].shift(1)
    )
    long_exit = (df["wvf"] < df["wvf_bb_mid"]) & (
        df["wvf"].shift(1) >= df["wvf_bb_mid"].shift(1)
    )
    short_entry = (df["iwvf"] > df["iwvf_bb_upper"]) & (
        df["iwvf"].shift(1) <= df["iwvf_bb_upper"].shift(1)
    )
    short_exit = (df["iwvf"] < df["iwvf_bb_mid"]) & (
        df["iwvf"].shift(1) >= df["iwvf_bb_mid"].shift(1)
    )
    df["long_entry"] = long_entry.fillna(False).astype(bool)
    df["short_entry"] = short_entry.fillna(False).astype(bool)
    df["long_exit"] = long_exit.fillna(False).astype(bool)
    df["short_exit"] = short_exit.fillna(False).astype(bool)
    return df
