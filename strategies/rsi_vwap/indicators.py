"""RSI(14) + session VWAP indicators.

Session VWAP anchored at each UTC-day boundary (00:00 UTC),
computed from typical price (h + l + c) / 3 weighted by
volume, resetting each UTC day -- the exact construction of
strategies/vwap_session_breakout (same cumulative-sum form,
same degenerate-band guard reasoning: on the first bar of a
session VWAP equals that bar's typical price, so the close
cannot be meaningfully above or below it and no signal can
fire there).

    VWAP = cumulative sum(tp * v) / sum(v) since the session start.

RSI(14) is Wilder RSI via base.rsi. Note the house-rule
caveat: base.rsi 0-fills on flat stretches (a flat run after
a rise prints RSI 0, after a fall prints 100); WARMUP = 40
suppresses the spin-up, and a genuinely flat stretch later
in the window can still print a 0/100 RSI -- the VWAP side
of the entry condition is unaffected.

Columns:
    vwap        -- session VWAP
    session_bar -- 1-based bar index within the UTC day
    rsi         -- Wilder RSI(14)
    atr14       -- ATR(14), diagnostic

No lookahead: every value on bar i uses data through bar i's
close only (cumulative sums include bar i and exclude
everything after it).
"""

import numpy as np
import pandas as pd

from strategies import base as B

RSI_N = 14


def add_indicators(
    df: pd.DataFrame,
    rsi_n: int = RSI_N,
) -> pd.DataFrame:
    df = df.copy()
    tp = (df["h"] + df["l"] + df["c"]) / 3.0
    v = df["v"]
    day = pd.Series(
        pd.to_datetime(df["t"], unit="ms", utc=True)
    ).dt.floor("D").to_numpy()
    cum_pv = (tp * v).groupby(day).cumsum()
    cum_v = v.groupby(day).cumsum()
    cum_v_safe = cum_v.replace(0, np.nan)
    vwap = cum_pv / cum_v_safe
    session_bar = pd.Series(np.arange(len(df))).groupby(day).cumcount().to_numpy() + 1
    df["vwap"] = vwap
    df["session_bar"] = session_bar
    df["rsi"] = B.rsi(df["c"], rsi_n)
    df["atr14"] = B.atr(df["h"], df["l"], df["c"], 14)
    return df
