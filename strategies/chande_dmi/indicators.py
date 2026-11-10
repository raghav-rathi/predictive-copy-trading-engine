"""Chande Dynamic Momentum Index (DMI) indicators.

Tushar Chande & Stanley Kroll, "The New Technical Trader"
(John Wiley & Sons, 1994). Formula reference:
https://docs.wickra.org/Indicators/Indicator-DynamicMomentumIndex

This DMI is Chande's Dynamic Momentum Index — a variable-length RSI —
and NOT Wilder's Directional Movement Index (same abbreviation,
different indicator).

Pipeline (all causal, bar i uses only data through bar i's close):
  vol_t     = stddev(close, 5)              (sample std, ddof=1)
  vol_avg_t = SMA(vol, 10)
  Vi_t      = vol_t / vol_avg_t             (1.0 if vol_avg is 0 or NaN)
  TD_t      = clamp(round(14 / Vi_t), 5, 30)  (dynamic lookback)
  DMI_t     = 100 * mean(gains over last TD_t changes)
                  / (mean(gains) + mean(losses) over last TD_t changes)
            using simple means of close-to-close changes (not Wilder
            smoothing), per the Wickra reference implementation of
            Chande's spec. If gains + losses == 0, DMI = 50.

DMI is bounded [0, 100]. DMI is NaN until enough bars exist for the
volatility ratio (14 bars) and the full dynamic lookback (up to 30
bars): the first valid DMI appears once i >= TD_i.
"""

import numpy as np
import pandas as pd

VOL_WINDOW = 5
VOL_AVG_WINDOW = 10
BASE_PERIOD = 14
TD_MIN = 5
TD_MAX = 30

INDICATOR_COLS = [
    "dmi_vol",
    "dmi_vol_avg",
    "dmi_vi",
    "dmi_td",
    "dmi",
]


def _dynamic_momentum_index(close: np.ndarray):
    """Compute (vol, vol_avg, vi, td, dmi) for a close array."""
    n = len(close)
    vol = np.full(n, np.nan)
    vol_avg = np.full(n, np.nan)
    vi = np.full(n, np.nan)
    td = np.full(n, np.nan)
    dmi = np.full(n, np.nan)

    c = pd.Series(close)
    vol = c.rolling(VOL_WINDOW, min_periods=VOL_WINDOW).std(ddof=1).to_numpy(dtype=float)
    vol_avg = (
        pd.Series(vol).rolling(VOL_AVG_WINDOW, min_periods=VOL_AVG_WINDOW).mean().to_numpy(dtype=float)
    )

    # Close-to-close changes; change j is c[j] - c[j-1], defined for j >= 1.
    changes = np.zeros(n)
    changes[1:] = close[1:] - close[:-1]
    gains = np.clip(changes, 0.0, None)
    losses = np.clip(-changes, 0.0, None)

    for i in range(n):
        if not np.isfinite(vol_avg[i]):
            continue
        if vol_avg[i] == 0.0:
            vi_i = 1.0
        elif np.isfinite(vol[i]):
            vi_i = vol[i] / vol_avg[i]
        else:
            vi_i = 1.0
        vi[i] = vi_i
        if vi_i <= 0.0:
            # Zero current volatility: 14 / 0 -> +inf, clamped to TD_MAX.
            td_i = TD_MAX
        else:
            td_i = int(round(BASE_PERIOD / vi_i))
            td_i = max(TD_MIN, min(TD_MAX, td_i))
        td[i] = float(td_i)
        # DMI over the last td_i changes (indices i-td_i+1 .. i).
        if i >= td_i:
            g = gains[i - td_i + 1 : i + 1].sum()
            l = losses[i - td_i + 1 : i + 1].sum()
            if g + l == 0.0:
                dmi[i] = 50.0
            else:
                dmi[i] = 100.0 * g / (g + l)

    return vol, vol_avg, vi, td, dmi


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    close = df["c"].to_numpy(dtype=float)
    vol, vol_avg, vi, td, dmi = _dynamic_momentum_index(close)
    df["dmi_vol"] = vol
    df["dmi_vol_avg"] = vol_avg
    df["dmi_vi"] = vi
    df["dmi_td"] = td
    df["dmi"] = dmi
    return df
