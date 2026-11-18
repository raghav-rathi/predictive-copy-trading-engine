"""London session breakout signals.

Long entry:  bar hour in [8,12), close > range_high, and it is the
             first break bar of the day (per side). If the first
             break bar of the day breaks both sides (its high above
             range_high AND its low below range_low), no entry that
             day.
Short entry: mirror (close < range_low, first break bar of the day).
Long exit:   close below range_low (opposite-side break) OR the bar
             hour == 16 (time exit, signal on the 16:00 bar).
Short exit:  close above range_high OR the bar hour == 16.

The harness risk layer's 2xATR stop / 2.5xATR trail also applies.
Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open). The range is only defined on
bars 08:00-16:00, so entries and opposite-side exits can only
fire inside the window; the 16:00 time exit fires on the hour
itself, where the range columns are NaN.
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    hour = df["hour"]
    c = df["c"]
    rh = df["range_high"]
    rl = df["range_low"]
    in_entry_window = (hour >= 8) & (hour < 12)
    long_break = (in_entry_window & (c > rh)).fillna(False)
    short_break = (in_entry_window & (c < rl)).fillna(False)
    both_break = ((df["h"] > rh) & (df["l"] < rl)).fillna(False)

    long_entry = pd.Series(False, index=df.index)
    short_entry = pd.Series(False, index=df.index)
    # First break bar per day per side; a both-sides break on the
    # first break bar voids the whole day.
    for _, idx in df.groupby("london_day").groups.items():
        idx = list(idx)
        first = None
        for i in idx:
            if bool(long_break.loc[i]) or bool(short_break.loc[i]):
                first = i
                break
        if first is None:
            continue
        if bool(both_break.loc[first]):
            continue
        if bool(long_break.loc[first]):
            long_entry.loc[first] = True
        elif bool(short_break.loc[first]):
            short_entry.loc[first] = True

    df["long_entry"] = long_entry.astype(bool)
    df["short_entry"] = short_entry.astype(bool)
    time_exit = (hour == 16)
    df["long_exit"] = (((c < rl).fillna(False)) | time_exit).astype(bool)
    df["short_exit"] = (((c > rh).fillna(False)) | time_exit).astype(bool)
    return df
