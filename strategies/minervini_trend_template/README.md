# Minervini Trend Template (SEPA gate)

Mark Minervini's Trend Template: a stock is only buyable when it
passes ALL eight conditions — the SEPA (Specific Entry Point
Analysis) gate. Traded here on 1h crypto bars, with the short
mirror added by the builder.

## The 8 conditions (long)

1. Price above the 150-period SMA.
2. Price above the 200-period SMA.
3. 150 SMA above the 200 SMA.
4. 200 SMA rising for at least 1 month — 720 bars on 1h, measured
   as SMA200[i] − SMA200[i−720] > 0.
5. 50 SMA above both the 150 and 200 SMAs.
6. Price above the 50 SMA.
7. Price ≥ 25% above its 52-week low.
8. Price within 25% of its 52-week high.
9. Relative Strength rating ≥ 70 — implemented as RSI(14) > 55,
   exactly as the MQL5 article does (there is no crypto RS rating).

## Entry / exit

- **Entry (long):** close above the trailing 20-bar high while
  the full gate holds — the breakout from a tight base/pivot.
  The harness executes at the next bar's open.
- **Exit (long):** close below the 50 SMA (trend violation), or
  an opposite short-gate breakdown, which flips the position.
- **Short mirror (builder-added):** all conditions inverted
  (price below SMA150/200, SMA150 below SMA200, SMA200 falling
  over 720 bars, SMA50 below both, price below SMA50, ≤ 25% below
  the trailing high, within 25% of the trailing low, RSI(14) <
  45); entry on a close below the trailing 20-bar low; exit on a
  close above the 50 SMA.

## Risk

Minervini's rule is a 7–8% stop below entry. RiskConfig only
offers an ATR-multiple stop, so 6×ATR is used: 1h ATR(14) on
BTC/ETH is typically ~0.8–1.5% of price, so 6×ATR ≈ 5–9%,
centred near the 7.5% target. This is an approximation — the stop
widens in volatile regimes and tightens in quiet ones. 8×ATR
chandelier trail, no fixed target (winners run), 720-bar (~30-day)
max hold, 1% risk per trade, 3× leverage cap. WARMUP = 960 bars
(SMA200 + 720-bar slope lookback, with margin).

## Honest flags

- The backtest window (~8 months) is shorter than 52 weeks, so
  conditions (7)/(8) use the longest trailing high/low available
  (expanding max/min over the full window to date), not a true
  52-week window. The gate is therefore weaker than the original:
  early in the window the "52-week low" is just the March low,
  which almost any later price clears by 25%.
- The 1h adaptation compresses Minervini's daily/weekly template
  by ~24×; a "1-month rising 200 SMA" on 1h bars is a much weaker
  trend statement than on daily bars.

Source: MQL5, "Automating Classic Market Methods (Part 4): Mark
Minervini's Trend Template" (http://mql5.com/en/articles/22790).
