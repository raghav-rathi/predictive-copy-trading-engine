"""Holy Grail (Linda Raschke & Larry Connors, "Street Smarts") indicators.

The setup buys the first pullback to the 20-bar EMA in a strong,
strengthening trend:

- ema20: the reference average price must touch
- adx(14): must be above the ADX threshold (shipped 30) AND rising
  (adx > adx[1]) -- a strong trend that is still gaining strength

A "touch" bar dips to the average but closes back on the trend side;
entry is a simulated buy-stop above (below) the touch bar's high (low),
triggered on the following bar. No lookahead: entry on bar i uses only
the touch bar i-1 and bar i's close.
"""

from strategies import base as B

EMA_LEN = 20
ADX_LEN = 14
ADX_THRESH = 30  # shipped entry threshold
ADX_EXIT = 20  # trend faded below this -> exit
ATR_LEN = 14


def add_indicators(df, adx_thresh: float = ADX_THRESH):
    df = df.copy()
    adx = B.adx(df["h"], df["l"], df["c"], ADX_LEN)
    df["adx"] = adx["adx"]
    df["plus_di"] = adx["plus_di"]
    df["minus_di"] = adx["minus_di"]
    df["ema20"] = B.ema(df["c"], EMA_LEN)
    df["atr"] = B.atr(df["h"], df["l"], df["c"], ATR_LEN)
    return df
