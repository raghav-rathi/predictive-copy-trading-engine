"""Alligator + Awesome Oscillator signals (Bill Williams Profitunity).

Long entry (all conditions on the same bar):
    * a confirmed up-fractal whose high is above the Alligator
      teeth, and the close CROSSES ABOVE that fractal high
      (cross-based, so it fires once per breakout, not every bar
      the close sits above the level)
    * AO > 0 and AO rising (green)
    * mouth open upward: lips > teeth > jaw
    The fractal level must be unchanged from the previous bar
    (level_stable): a newly confirmed fractal can move the
    forward-filled level, and a cross judged against a level
    that just jumped would be a bookkeeping artifact, not a
    price breakout.

Short entry: mirror -- confirmed down-fractal below the teeth,
close crosses below its low, AO < 0 and falling (red),
lips < teeth < jaw.

Exit: long exits on a close back below the lips (price fell
inside the mouth) OR AO red for 2 consecutive bars OR the
opposite entry; short mirrors (close above the lips, AO green
for 2 consecutive bars, opposite entry). The house 2xATR hard
stop / 3xATR trail sit behind these exits, with a 120-bar max
hold.

Signal columns are boolean, no NaN, no lookahead (execution
at next-bar open is handled by the harness).
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    c = df["c"]
    ao = df["ao"]
    ao_green = df["ao_green"]
    ao_red = df["ao_red"]

    up_level = df["frac_up_level_ff"]
    up_stable = (up_level == up_level.shift(1)).fillna(False)
    long_entry = (
        crossed_above(c, up_level)
        & up_stable
        & (up_level > df["teeth"])
        & (ao > 0)
        & ao_green
        & (df["lips"] > df["teeth"])
        & (df["teeth"] > df["jaw"])
    ).fillna(False)

    down_level = df["frac_down_level_ff"]
    down_stable = (down_level == down_level.shift(1)).fillna(False)
    short_entry = (
        crossed_below(c, down_level)
        & down_stable
        & (down_level < df["teeth"])
        & (ao < 0)
        & ao_red
        & (df["lips"] < df["teeth"])
        & (df["teeth"] < df["jaw"])
    ).fillna(False)

    ao_red_2 = ao_red & ao_red.shift(1).fillna(False)
    ao_green_2 = ao_green & ao_green.shift(1).fillna(False)
    long_exit = (
        (c < df["lips"]) | ao_red_2 | short_entry
    ).fillna(False)
    short_exit = (
        (c > df["lips"]) | ao_green_2 | long_entry
    ).fillna(False)

    df["long_entry"] = long_entry.to_numpy(bool)
    df["short_entry"] = short_entry.to_numpy(bool)
    df["long_exit"] = long_exit.to_numpy(bool)
    df["short_exit"] = short_exit.to_numpy(bool)
    return df
