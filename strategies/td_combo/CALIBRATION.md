# TD Combo — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-14 → 2026-10-18, same costs/sizing). One variant against the
shipped config. Throwaway sweep script: `/tmp/batch9_calibration.py`
(results only; indicators/risk unchanged).

| Variant | Coin | Trades | Win% | Net $ | Sharpe | PF |
|---|---|---|---|---|---|---|
| shipped (1.0xATR stop) | BTC | 5 | 60.0% | +$19 | +0.10 | 1.08 |
| shipped (1.0xATR stop) | ETH | 4 | 75.0% | +$431 | +1.55 | 4.63 |
| shipped (1.0xATR stop) | HYPE | 6 | 50.0% | -$19 | -0.07 | 0.94 |
| variant (2.0xATR stop) | BTC | 5 | 60.0% | -$90 | -0.69 | 0.58 |
| variant (2.0xATR stop) | ETH | 4 | 75.0% | +$164 | +1.16 | 2.51 |
| variant (2.0xATR stop) | HYPE | 6 | 66.7% | +$43 | +0.35 | 1.36 |

## One-line verdict

- **2.0xATR stop:** wider stop keeps the same 15 trades alive longer but
  degrades BTC (flips to -$90) and ETH (drops to +$164) while helping
  HYPE marginally. With 4–6 trades per coin every one of these numbers
  is a single trade away from reversing, so the variant proves nothing
  except that the shipped 1.0xATR stop is no worse than the alternative.
- **Shipped decision:** keep the specified 1.0xATR stop; the sweep is
  diagnostic, not an adoption. The real calibration question for TD
  Combo is bar speed (daily vs 1h), not the stop multiple.
