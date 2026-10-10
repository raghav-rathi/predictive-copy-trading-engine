# Darvas Box — Calibration Sweep

Two-variant robustness sweep on the same HL 1h data (BTC + ETH + HYPE,
2026-03-14 → 2026-10-09). Shipped config = 60-bar box window, breakout
volume > 1.25x SMA(20).

| Variant | Box window | Vol filter | Trades | Combined net $ | BTC net $ | ETH net $ | HYPE net $ |
|---|---|---|---|---|---|---|---|
| shipped | 60 | 1.25x | 107 | +$1,980 | -$1,170 | +$2,707 | +$443 |
| window-30 | 30 | 1.25x | 157 | +$294 | -$1,336 | +$1,780 | -$151 |
| vol-1.0x | 60 | 1.0x | 112 | +$1,626 | -$1,170 | +$2,612 | +$183 |

## One-line verdicts

- **window-30: worse.** 50% more trades, worse on every coin — ETH profit
  falls from +$2,707 to +$1,780, HYPE flips from +$443 to -$151, and BTC's
  drawdown deepens to -24.9%. Shorter boxes get faked out more; the 60-bar
  level is load-bearing.
- **vol-1.0x: marginally worse.** Loosening the filter adds 5 trades
  (107 → 112) and shaves $354 off combined PnL; the extra entries are net
  losers, so the 1.25x expansion requirement earns its keep. (Note: on BTC
  the filter never bound — identical 37 trades — the BTC losses are the
  box mechanism failing in chop, not a volume-filter problem.)

## Conclusion

Keep the shipped config (60-bar window, 1.25x volume). The parameter
choices are directionally robust — both perturbations degrade the result —
but the strategy's real weakness is structural, not parametric: it needs
trending, range-breaking markets, and this window's BTC gave it none.
