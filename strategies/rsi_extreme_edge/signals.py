"""RSI extreme-edge fade signals (mechanism from @Vision33X, rsi-extreme-edge,
138 live trades on BloFin, 2026 — summarized in our own words).

Exhaustion fade on 1H, RSI(14):
  SHORT: RSI was above 90 last bar and crosses back below 90 on this bar
         (the "cross-back" confirming bar) -> short.
  LONG:  RSI was below 10 last bar and crosses back above 10 on this bar
         -> long.
Any excursion past the extreme followed by a cross-back qualifies; entries
execute at the next bar's open per the harness convention (the author's
"close of the confirming bar" is one bar earlier — documented approximation).

COIN_FILTER parameterizes the author's coin-personality findings as a
per-coin long/short allowlist. Default: both directions on all coins; the
backtest script can pass coin= to apply a filter variant.
"""

import pandas as pd

from strategies.rsi_extreme_edge.indicators import RSI_LONG_LEVEL, RSI_SHORT_LEVEL

COIN_FILTER: dict[str, tuple[str, ...]] = {
    "BTC": ("long", "short"),
    "ETH": ("long", "short"),
    "HYPE": ("long", "short"),
}


def add_signals(df: pd.DataFrame, coin: str | None = None) -> pd.DataFrame:
    df = df.copy()
    short_setup = (df["rsi"] < RSI_SHORT_LEVEL) & (
        df["rsi_prev"] > RSI_SHORT_LEVEL
    )
    long_setup = (df["rsi"] >= RSI_LONG_LEVEL) & (
        df["rsi_prev"] < RSI_LONG_LEVEL
    )
    sides = COIN_FILTER.get(coin, ("long", "short")) if coin else ("long", "short")
    df["long_entry"] = long_setup & ("long" in sides)
    df["short_entry"] = short_setup & ("short" in sides)
    # Signal exits: none — the ATR stop, 1.5xSL target, and 72-bar max hold
    # manage every trade.
    df["long_exit"] = False
    df["short_exit"] = False
    for col in ("long_entry", "short_entry", "long_exit", "short_exit"):
        df[col] = df[col].fillna(False)
    return df
