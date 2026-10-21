# Klinger Volume Oscillator — Calibration

Signal-line sensitivity on the same Hyperliquid 1h data as BACKTEST.md
(BTC/ETH/HYPE, 2026-03-14 → 2026-10-21, same costs/sizing, 2xATR stop,
3xATR trail, 150-bar max hold). The signal line smooths kvo: 9 reacts
fastest (more crosses, more whipsaw), 21 slowest (fewer trades, later
exits). The sweep re-runs `add_indicators(df, signal_n=X)` only —
signals and risk are unchanged.

| Signal | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 9 | BTC | 902 | 44.3% | -$7,103 | -7.06 | 0.58 | -$7.88 |
| 9 | ETH | 815 | 47.1% | -$5,567 | -4.25 | 0.71 | -$6.83 |
| 9 | HYPE | 756 | 50.3% | -$3,697 | -2.84 | 0.82 | -$4.89 |
| 13 (shipped) | BTC | 761 | 47.3% | -$6,170 | -5.60 | 0.63 | -$8.11 |
| 13 (shipped) | ETH | 681 | 46.8% | -$4,905 | -3.67 | 0.72 | -$7.20 |
| 13 (shipped) | HYPE | 680 | 52.8% | -$2,692 | -1.92 | 0.86 | -$3.96 |
| 21 | BTC | 687 | 47.6% | -$5,853 | -5.26 | 0.63 | -$8.52 |
| 21 | ETH | 597 | 46.4% | -$4,550 | -3.47 | 0.70 | -$7.62 |
| 21 | HYPE | 596 | 50.7% | -$2,848 | -2.13 | 0.84 | -$4.78 |

## One-line verdict

- **9:** worst everywhere (-$16,367 combined, BTC MaxDD -71.6%):
  reacting faster to a saturating oscillator just adds more losers.
- **21:** slightly better on BTC/ETH (-$5,853/-$4,550 vs -$6,170/-$4,905)
  but worse on HYPE (-$2,848 vs -$2,692) — combined -$13,251, still
  deeply red. Smoothing the cross delays entries into an already-dead
  move; there is no sweet spot.
- **13:** best combined (-$13,767) and least-bad on every coin — but
  that is an in-sample observation about a loser, not a justification.
- **Shipped decision:** keep the specified signal=13 as the registry
  config regardless. The 13 was fixed before any backtest was run; it
  happens to be the least-bad in-sample setting here, and adopting it
  *because* of that would still be in-sample selection. The honest
  read: the signal line is not the problem — no setting makes the
  strategy positive, so the failure is in the volume-force
  construction itself (see BACKTEST.md verdict).
