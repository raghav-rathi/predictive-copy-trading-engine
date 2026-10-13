# Wilder DMI — Calibration

Sweeps run on the same data as BACKTEST.md (Hyperliquid 1h, 2026-03-14 →
2026-10-13, use_funding=False). Totals are summed net PnL across BTC+ETH+HYPE.

## Sweep results

| param | value | total $ | BTC $ | ETH $ | HYPE $ |
|-------|-------|---------|-------|-------|--------|
| adx_min | 20.0 | -281 | -179 (16t) | -557 (10t) | 455 (10t) |
| adx_min | **25.0** (published) | 686 | -120 (3t) | -105 (1t) | 911 (4t) |
| adx_min | 30.0 | 782 | 0 (0t) | 0 (0t) | 782 (3t) |
| adx_dead | 15.0 / **20.0** / 25.0 | 686 | identical — no trade ever hit the ADX-dead exit |
| max_hold | 60 / **120** / 240 | 686 | identical — no trade ever reached max hold |

## Decision

- **Shipped the published classic params: ADX > 25 and rising for entries,
  ADX < 20 for exits.** No sweep alternative is stable or meaningful: loosening
  the gate to 20 triples the trade count but turns the total negative (-$281);
  tightening to 30 kills all BTC/ETH trades. The exit sweeps change nothing
  because SAR flips / the range rule always fired first.
- Stated plainly: with 8 total trades, this sweep cannot calibrate anything —
  the classic ships by default and the strategy stays research-grade
  (see BACKTEST.md).
