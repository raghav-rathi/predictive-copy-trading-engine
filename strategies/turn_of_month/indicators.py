"""Turn-of-the-month calendar indicators.

Long-only calendar effect (Lakonishok & Smidt window): enter on
the first bar of the last calendar day of each month and exit on
the 23:00 UTC bar of the 3rd calendar day of the next month.

Date logic uses ONLY the bar timestamp t (UTC) — never wall-clock
time. The harness executes a signal generated on bar i at bar
i+1's open, so the entry signalled on the 00:00 UTC bar of the
last day fills at the 01:00 UTC open, and the exit signalled on
the 23:00 UTC bar of day 3 fills at the 00:00 UTC open of day 4.

If a month's 00:00 bar (last day) or 23:00 bar (day 3) is missing
from the data, that month simply produces no entry / no signal
exit for that leg; the harness max hold (120 bars) bounds the
holding period.

Columns:
    cal_day / cal_hour -- UTC calendar day / hour of the bar
    days_in_month      -- days in the bar's UTC calendar month
    last_day_of_month  -- True on the last calendar day
    tom_entry          -- True only on the 00:00 UTC bar of the
                          last calendar day (long entry signal)
    tom_exit           -- True only on the 23:00 UTC bar of the
                          3rd calendar day (long exit signal)

No lookahead: every value on bar i uses only bar i's timestamp.
"""

import pandas as pd

INDICATOR_COLS = ["cal_day", "cal_hour", "days_in_month",
                  "last_day_of_month", "tom_entry", "tom_exit"]


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    dt = pd.to_datetime(df["t"], unit="ms", utc=True)
    df["cal_day"] = dt.dt.day.astype(int)
    df["cal_hour"] = dt.dt.hour.astype(int)
    df["days_in_month"] = dt.dt.days_in_month.astype(int)
    df["last_day_of_month"] = df["cal_day"] == df["days_in_month"]
    df["tom_entry"] = (df["last_day_of_month"] & (df["cal_hour"] == 0)).astype(bool)
    df["tom_exit"] = ((df["cal_day"] == 3) & (df["cal_hour"] == 23)).astype(bool)
    return df
