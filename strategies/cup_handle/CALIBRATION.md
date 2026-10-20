# Cup and Handle Breakout — Calibration

Breakout-volume sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, 2026-03-14 → 2026-10-20, same costs/sizing,
1.5xATR stop, 4.0xATR target, 120-bar max hold). The knob is the volume
multiple vs the 20-bar average required on the breakout bar.

| Volume | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 1.4x (shipped) | BTC | 0 | — | $0 | — | — | — |
| 1.4x (shipped) | ETH | 0 | — | $0 | — | — | — |
| 1.4x (shipped) | HYPE | 0 | — | $0 | — | — | — |
| 1.2x | BTC | 0 | — | $0 | — | — | — |
| 1.2x | ETH | 0 | — | $0 | — | — | — |
| 1.2x | HYPE | 0 | — | $0 | — | — | — |
| 1.6x | BTC | 0 | — | $0 | — | — | — |
| 1.6x | ETH | 0 | — | $0 | — | — | — |
| 1.6x | HYPE | 0 | — | $0 | — | — | — |

## One-line verdict

- The volume knob changes nothing: 0 trades at every setting on every
  coin. The binding constraint is upstream — the dual cup-depth filter
  (8–25% of rim AND 1–4x ATR) admits zero candidates on 1h crypto (see
  BACKTEST.md: median cup depth is ~20x ATR, so the ATR band rejects
  everything before volume is ever checked).
- **Shipped decision:** keep the specified 1.4x volume confirmation.
  There is no in-sample winner to adopt, and relaxing the depth filter
  to manufacture trades would be redesigning the pattern on this
  window, not calibrating it. The honest next step is a timeframe-aware
  reformulation (daily bars, or an ATR-only depth band) validated out
  of sample.
