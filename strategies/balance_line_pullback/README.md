# Balance Line Pullback (Bill Williams)

Bill Williams' Balance Line trade (the 5th dimension of
Profitunity, "Trading Chaos" / "New Trading Dimensions"):
the Balance Line is the Alligator's Jaw, SMMA(13) of the
median price; price pulls back to its balance and the
trend resumes. This engine trades the pullback to the Jaw
with the Alligator mouth as the trend gate.

- **median:** (h + l) / 2
- **jaw:** SMMA(median, 13) -- the Balance Line
- **teeth:** SMMA(median, 8)
- **lips:** SMMA(median, 5)
- **Mouth open up:** lips > teeth > jaw; **mouth open down:**
  lips < teeth < jaw
- **Touch:** a bar low inside [jaw - 0.5*ATR(14),
  jaw + 0.5*ATR(14)] (longs); a bar high inside the same
  band (shorts)
- **LONG:** a touch within the last 5 bars AND close > jaw
  AND close > prior close AND mouth open up
- **SHORT:** a touch (bar high) within the last 5 bars AND
  close < jaw AND close < prior close AND mouth open down
- **Entry fires once per pullback:** the turn condition
  must be true on this bar and false on the prior bar
  (first-bar-of-run guard), so it never stays True for
  consecutive bars while price rides above the jaw.
- **Exit:** long exits when the close crosses BELOW the jaw
  (price lost its balance) or the lips cross below the
  teeth (mouth closing), or the opposite entry fires;
  short mirrors. 2xATR hard stop, 3xATR trail, 96-bar max
  hold behind them.
- **Risk:** 2xATR hard stop, 3xATR chandelier trail, 96-bar
  max hold, 1% risk/trade, 3x leverage

Parameters: SMMA 13/8/5 on median price, touch tolerance
0.5xATR(14), touch window 5 bars. Entries are
cross-flavoured (first bar of a turn-condition run),
never plain level conditions -- a level condition would
re-fire every bar price sat beyond the jaw.

Deviations / implementation notes (all documented, none
tuned to PnL):

- The book displaces the Alligator lines 8/5/3 bars into
  the future for plotting. Those shifted values are NOT
  used here -- UNSHIFTED SMMA values only. Using the
  forward displacement in a live signal would be lookahead
  (it needs future bars); the displacement is a charting
  convention, not a trading rule. Same deviation as the
  batch-48 precedent in alligator_awesome_combo.
- SMMA[i] = (SMMA[i-1]*(n-1) + price[i]) / n, seeded with
  the simple average of the first n prices -- the same
  pattern as strategies/alligator_awesome_combo.
- The "touch within the last 5 bars" window is the shipped
  reading of "price pulls back to its balance and turns";
  the book does not fix a number of bars.

This is DISTINCT from the existing ema_pullback (EMA(20)
touch + EMA(50) trend): different line (SMMA-13 of
median price -- the Balance Line -- not an EMA of close),
different trend gate (Alligator mouth alignment, not a
single EMA), different source (Bill Williams Profitunity,
not a generic EMA pullback).

Sources: Bill Williams, "Trading Chaos" / "New Trading
Dimensions" -- Balance Line trades --
https://www.forexfactory.com/thread/26044-profitunity-chaos-trading-system-by-bill-williams?page=83

Usage:

```python
from strategies.balance_line_pullback import indicators, signals, risk

df = indicators.add_indicators(df)  # touch_tol=0.5, touch_window=5 default
sig = signals.add_signals(df)  # require_mouth=True default
```

See BACKTEST.md for the 2026-03-14 -> 2026-11-27 Hyperliquid 1h
(BTC/ETH/HYPE, batch-49 pinned window) results and
CALIBRATION.md for the touch-tolerance (0.5/1.0xATR) and
mouth-gate (required / jaw-only) sensitivity checks.
