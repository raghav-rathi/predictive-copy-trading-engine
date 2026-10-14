# Connors RSI(2) — Robustness sweep

Shipped baseline: RSI(2) 10/90 entries, 3-bar streak, 70/30 + SMA50 exits,
2.5xATR stop, 30-bar max hold. Same data/costs/sizing as BACKTEST.md
(HL 1h, BTC + ETH + HYPE, 2026-03-14 → 2026-10-10, 0.045% fee + 0.01%
slippage per side, 1% risk/trade, $10k start).

| Variant | Trades | Win% range | Net $ (BTC/ETH/HYPE) | Combined Net $ | Sharpe range | PF range |
|---|---|---|---|---|---|---|
| Baseline 10/90, streak=3 | 641 | 44.9–45.9% | -1340 / -1254 / -1079 | **-3,673** | -3.76..-2.78 | 0.51–0.68 |
| A: strict 5/95, streak=3 | 395 | 40.8–47.3% | -649 / -1203 / -506 | **-2,358** | -3.41..-1.75 | 0.42–0.74 |
| B: loose 15/85, streak=3 | 795 | 46.1–46.8% | -1719 / -1670 / -1365 | **-4,754** | -4.11..-3.16 | 0.52–0.66 |
| C: 10/90, streak=2 bars | 881 | 43.1–46.0% | -2394 / -1715 / -1375 | **-5,484** | -5.45..-3.27 | 0.45–0.68 |

## One-line verdicts

- **A (strict 5/95): least bad, still a loser.** Halves the trade count and
  cuts combined loss ~36% vs baseline, but every coin stays negative with
  ETH still -12.0% — tighter thresholds just take fewer losing trades.
- **B (loose 15/85): worse.** 24% more trades, 29% larger combined loss —
  looser entries catch pullbacks earlier and sit through deeper drawdowns
  the SMA(50) filter was supposed to kill.
- **C (streak=2): worst.** Nearly triple the baseline trade count, -24.3%
  max DD on BTC — the streak is the only timing discipline in the system,
  and weakening it turns the entry into "any RSI(2) washout in a trend."
- **Overall:** failure is structural, not parametric. No threshold or
  streak tweak flips the sign on any coin; the exit pair (RSI reversal +
  SMA50 cut) chokes winners on 1h bars. Strategy shelved, not shipped.
