# DeMarker exhaustion — Calibration (robustness sweep)

Swept two variants against the shipped config (DeM(14), entries at
0.3/0.7 crosses, exits at 0.5 crosses, 2xATR stop, 24-bar max hold),
same data (HL 1h, BTC/ETH/HYPE, 2026-03-14 → 2026-10-10), same costs
(0.045% fee + 0.01% slippage per side) and sizing (1% risk, 3x cap, $10k).

| Variant | Trades | Combined net $ | BTC net% / PF | ETH net% / PF | HYPE net% / PF |
|---|---|---|---|---|---|
| Shipped (period 14, exit 0.5) | 737 | -$8,143 | -29.3% / 0.73 | -17.1% / 0.83 | -35.0% / 0.63 |
| A: period 9 | 1,175 | -$10,235 | -40.2% / 0.70 | -29.6% / 0.77 | -32.6% / 0.74 |
| B: period 14, exit 0.6/0.4 | 720 | -$8,094 | -31.1% / 0.74 | -16.5% / 0.85 | -33.4% / 0.68 |

## One-line verdicts

- **Variant A (period 9): WORSE.** A faster DeM crosses the bands 60%
  more often (1,175 vs 737 trades), multiplying fee drag to ~$8k, and the
  profit factor doesn't improve on any coin — shorter lookback = more
  noise, not more edge.
- **Variant B (exit 0.6/0.4): marginally less bad, still a LOSER.**
  Combined PnL improves by ~$49 (-$8,094 vs -$8,143) on 17 fewer trades —
  letting winners run a little longer helps at the margin, but every coin
  stays deeply negative with profit factor < 0.9.
- **Structural conclusion: ship nothing.** No parameter direction rescues
  this: the 1h DeM exhaustion cross fires repeatedly into trending legs
  (each cross re-enters full size) while the mean-reversion exit clips
  the bounce. A daily-bar or higher-conviction filter (e.g. require an
  RSI < 20 confirmation, or trade only after a >=3xATR impulse) would be
  a different strategy, not a calibration of this one.
