"""Holy Grail signals (Linda Raschke & Larry Connors, "Street Smarts").

Long regime:  c > ema20 & adx > threshold & adx rising
Long touch:   regime & (l <= ema20) & (c > ema20)      -- dip to the
              average, close back on the trend side
Long entry:   on bar i when touch_{i-1} & c_i > h_{i-1}
              (simulated buy-stop above the touch bar's high)
Short is the mirror image.

Exits: the setup is dead when price closes back through the average
or when ADX falls under 20 (the trend faded). Risk-level exits
(stop/trail/max hold) come from risk.py.
"""

import pandas as pd

from strategies.lbr_holy_grail.indicators import ADX_EXIT, ADX_THRESH


def add_signals(df: pd.DataFrame, adx_thresh: float = ADX_THRESH) -> pd.DataFrame:
    df = df.copy()
    c, h, l = df["c"], df["h"], df["l"]
    ema20, adx = df["ema20"], df["adx"]
    adx_rising = (adx > adx.shift(1)).fillna(False)

    regime_l = (c > ema20) & (adx > adx_thresh) & adx_rising
    regime_s = (c < ema20) & (adx > adx_thresh) & adx_rising

    touch_l = regime_l & (l <= ema20) & (c > ema20)
    touch_s = regime_s & (h >= ema20) & (c < ema20)

    df["long_entry"] = (
        touch_l.shift(1).fillna(False) & (c > h.shift(1))
    ).fillna(False)
    df["short_entry"] = (
        touch_s.shift(1).fillna(False) & (c < l.shift(1))
    ).fillna(False)
    df["long_exit"] = ((c < ema20) | (adx < ADX_EXIT)).fillna(False)
    df["short_exit"] = ((c > ema20) | (adx < ADX_EXIT)).fillna(False)
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False).astype(bool)
    return df
