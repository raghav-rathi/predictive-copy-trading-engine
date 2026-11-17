"""Ichimoku + MACD signals.

Long entry:  close above the cloud (above BOTH Senkou A and
             Senkou B as plotted at bar i) AND Tenkan crosses
             above Kijun AND MACD histogram > 0.
Short entry: close below the cloud (below both spans) AND
             Tenkan crosses below Kijun AND MACD histogram < 0.
Long exit:   Tenkan crosses below Kijun OR the close is no
             longer above the cloud (close <= the higher span —
             it has entered the cloud or fallen below it).
Short exit:  Tenkan crosses above Kijun OR the close is no
             longer below the cloud (close >= the lower span).

"Above the cloud" is a strict comparison against both spans;
the cloud-top / cloud-bottom comparisons in the exits use the
max / min of the two spans, so a thick cloud and a thin cloud
are handled the same way. NaN cloud values (before the
displacement window fills) compare False, so no entry can fire
before the cloud exists.

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd

from strategies import base as B


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    sa = df["senkou_a"]
    sb = df["senkou_b"]
    tk = df["tenkan"]
    kj = df["kijun"]
    hist = df["macd_hist"]
    above_cloud = (c > sa) & (c > sb)
    below_cloud = (c < sa) & (c < sb)
    tk_cross_up = B.crossed_above(tk, kj)
    tk_cross_down = B.crossed_below(tk, kj)
    cloud_top = pd.concat([sa, sb], axis=1).max(axis=1)
    cloud_bottom = pd.concat([sa, sb], axis=1).min(axis=1)
    long_entry = (above_cloud & tk_cross_up & (hist > 0)).fillna(False).astype(bool)
    short_entry = (below_cloud & tk_cross_down & (hist < 0)).fillna(False).astype(bool)
    long_exit = (tk_cross_down | (c <= cloud_top)).fillna(False).astype(bool)
    short_exit = (tk_cross_up | (c >= cloud_bottom)).fillna(False).astype(bool)
    df["long_entry"] = long_entry
    df["short_entry"] = short_entry
    df["long_exit"] = long_exit
    df["short_exit"] = short_exit
    return df
