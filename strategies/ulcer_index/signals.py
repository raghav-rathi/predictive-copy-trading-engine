"""Ulcer Index regime-gated breakout, long only.

The UI is a downside-risk gauge: it reads ~0 in calm uptrends and
spikes when selling pressure hits. So the strategy only buys
breakouts *in calm regimes*:

    long_entry = (ulcer.shift(1) < 5.0) & crossed_above(close, donchian_high_20.shift(1))
    long_exit  = crossed_below(close, donchian_low_10.shift(1)) | (ulcer > 10.0)

The entry is a 20-bar Donchian breakout gated on regime calm; the
gate reads the *prior-bar* ulcer because a breakout to a new high
becomes the trailing peak on its own bar, inflating the current-bar
read — gating on the current bar would veto every entry. The exit
is the classic 10-bar Donchian low OR a panic spike of the UI —
if downside volatility suddenly spikes above 10, the calm-regime
premise is broken, so get out even if price hasn't hit the exit
level yet. Crosses are taken against the *prior-bar* Donchian
level (shift(1)) so the signal on bar j uses only information
available at bar j's close; the harness executes at the next bar's
open.

No shorts: UI says nothing about upside exhaustion, so allow_shorts
is False in risk.py and short columns are all-False here (the
harness ignores short entries anyway; the explicit columns keep
the signal contract uniform).

Signal columns are boolean, no NaN, no lookahead.
"""

import pandas as pd

from strategies.base import crossed_above, crossed_below

CALM_THRESHOLD = 5.0    # regime gate for entries
PANIC_THRESHOLD = 10.0  # hard exit trigger


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    ui = df["ulcer"]
    brk_up = crossed_above(df["c"], df["donchian_high_20"].shift(1)).fillna(False)
    brk_dn = crossed_below(df["c"], df["donchian_low_10"].shift(1)).fillna(False)
    # Regime gate on the PRIOR bar: a breakout bar is the trailing peak
    # on its own bar, so current-bar ulcer would veto every entry.
    calm = (ui.shift(1) < CALM_THRESHOLD).fillna(False)
    panic = (ui > PANIC_THRESHOLD).fillna(False)
    df["long_entry"] = (brk_up & calm).astype(bool)
    df["short_entry"] = pd.Series(False, index=df.index).astype(bool)
    df["long_exit"] = (brk_dn | panic).astype(bool)
    df["short_exit"] = pd.Series(False, index=df.index).astype(bool)
    return df
