# Minervini Trend Template — Calibration

All parameters were fixed **a priori** from the published
Minervini template and 1h-bar reasoning — there is no in-sample
sweep, so there is nothing to select on this window.

| Parameter | Value | Rationale |
|---|---|---|
| SMA lengths | 50 / 150 / 200 | the template's own lengths, carried over unchanged |
| 200-SMA rising window | 720 bars (~1 month on 1h) | the article's "rising for at least 1 month", scaled 30 days × 24 bars |
| 52-week low premium | ≥ 25% above trailing low | the template's 25–30% band, lower end (a 1h crypto low is noisier than a daily equity low) |
| 52-week high proximity | within 25% of trailing high | the template's own 25% band |
| RS proxy | RSI(14) > 55 long / < 45 short | the MQL5 article's own substitution for the RS rating ≥ 70; 45 is the symmetric mirror |
| Breakout window | 20 bars | a tight base on 1h bars; the pivot/breakout entry of the SEPA method |
| Stop | 6×ATR(14) | approximates Minervini's 7–8% stop: 1h ATR(14) is typically ~0.8–1.5% of price, so 6×ATR ≈ 5–9%, centred near 7.5%. **Deviation:** RiskConfig has no fixed-% stop, so this is an ATR translation, not the literal rule — the stop widens in volatile regimes and tightens in quiet ones |
| Trail | 8×ATR chandelier | wider than the stop so a running trend is not trailed out by its own noise; lets winners run per the method |
| Target | none | Minervini lets winners run; the 50-SMA violation is the exit |
| Max hold | 720 bars (~30 days) | a SEPA breakout that has not run in a month was not a SEPA move |
| Risk | 1% / trade, 3× leverage cap | house standard |
| Warmup | 960 bars | SMA(200) + 720-bar slope lookback, with margin |

## Deviations from the source, stated plainly

1. **52-week window exceeds the backtest window.** Conditions
   (7)/(8) use the expanding trailing high/low over the full
   window to date (~8 months max), not a true 52-week window.
   The gate is weaker than the original, especially early in the
   window.
2. **RS rating → RSI(14) > 55.** No crypto equivalent of
   Minervini's Relative Strength rating exists; the substitution
   is the MQL5 article's own, not ours.
3. **7–8% stop → 6×ATR.** See the stop row above.
4. **Short mirror is builder-added.** Minervini's template is
   long-only; the inverted gate is our symmetric extension.
5. **Daily/weekly template on 1h bars.** Every "day" in the
   original becomes 24 bars here; trend persistence on 1h is a
   weaker statement than on daily bars.

No optimization was performed, and the window in BACKTEST.md must
not be used to tune any of these numbers.
