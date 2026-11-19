"""ATR-percentile volatility regime signals.

Expansion (ATR percentile > 0.60): Donchian(20) breakout — long
on a close above the prior 20-bar high (excluding the current
bar), short on a close below the prior 20-bar low. Exit on a
close back inside the channel midpoint, or on the opposite break.
Compression (ATR percentile < 0.40): Bollinger(20, 2) fade —
long on a close below the lower band, short on a close above the
upper band. Exit on a close back to the mid (above the mid for a
long, below the mid for a short). Middle regime (0.40-0.60): no
entries and no signal exits; the position is carried by the
harness stop / trail / max hold.

Exits follow the regime in force on the signal bar, so a trade
opened in one regime is exited by the new regime's rules if the
regime flips mid-trade.

Signal columns are boolean, no NaN, no lookahead (the harness
executes at the next bar's open).
"""

import pandas as pd


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    atr_pct = df["atr_pct"]
    expansion = (atr_pct > 0.60).fillna(False)
    compression = (atr_pct < 0.40).fillna(False)

    c = df["c"]
    prev_high = df["prev_high"]
    prev_low = df["prev_low"]
    mid = df["donchian_mid"]
    bb_mid = df["bb_mid"]
    bb_upper = df["bb_upper"]
    bb_lower = df["bb_lower"]

    df["long_entry"] = (
        (expansion & (c > prev_high)) | (compression & (c < bb_lower))
    ).fillna(False).astype(bool)
    df["short_entry"] = (
        (expansion & (c < prev_low)) | (compression & (c > bb_upper))
    ).fillna(False).astype(bool)
    df["long_exit"] = (
        (expansion & ((c < mid) | (c < prev_low)))
        | (compression & (c > bb_mid))
    ).fillna(False).astype(bool)
    df["short_exit"] = (
        (expansion & ((c > mid) | (c > prev_high)))
        | (compression & (c < bb_mid))
    ).fillna(False).astype(bool)
    return df
