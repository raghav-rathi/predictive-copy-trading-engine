# Pennant Pattern

## Mechanism

The classic pennant continuation (Edwards & Magee / StockCharts)
as a causal state machine:

1. **Pole** — a completed 5-bar close move of at least 3x ATR(14).
   "Completed" means the pole's last bar stalled (|close change|
   <= 0.5x ATR), so a steady trend cannot trigger mid-pole.
2. **Consolidation** — 5–15 bars after the pole bar. Convergence
   is tested from the 5th consolidation bar onward by comparing
   3-bar blocks: the last 3 bars' high-max must be below the
   previous 3 bars' high-max (successive highs falling) and the
   last 3 bars' low-min above the previous 3 bars' low-min
   (successive lows rising). When convergence holds, the setup
   arms and the range freezes at the consolidation's high/low.
3. **Breakout** — a close beyond the frozen range (high for bull,
   low for bear) with volume above 1.2x the prior 20-bar average
   volume (the average excludes the current bar).

## Entry / exit rules

- **Long entry:** bull pennant armed + close above range high +
  volume > 1.2x 20-bar average.
- **Short entry:** bear pennant armed + close below range low +
  volume > 1.2x 20-bar average.
- **Exit:** the opposite direction's volume-confirmed breakout,
  or the 168-bar (~7-day) max hold. A failed breakout (close back
  inside the range) is left to the 2xATR stop / 2.5xATR trail.
- An armed setup dies without a trade if price breaks the range's
  far side by more than 0.5x ATR (invalidation) or if 15 bars pass
  without a breakout (expiry).
- Risk layer: 2xATR hard stop, 2.5xATR chandelier trail, no fixed
  target, 1% equity risk per trade, 3x leverage cap.

## Source

Classic pennant continuation — Edwards & Magee (*Technical
Analysis of Stock Trends*), StockCharts chart-school description.

## Honest caveats

- Pennants are rare at 1h under this strict definition: 24 trades
  across three coins in seven months (see BACKTEST.md). The
  volume filter kills many breakouts that price alone would have
  taken — that is the design, not a bug, but it means the sample
  is thin.
- BTC and ETH legs are slightly green while HYPE is sharply
  negative (profit factor 0.04 on 6 trades); the combined result
  is slightly negative, so no coin-level story survives.
- The breakout bar's close is the entry trigger and the harness
  executes at the next bar's open, so fast breakouts give back
  the first bar of the move before entry.
