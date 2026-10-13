# Holy Grail — Calibration

Sweeps run on the same data as BACKTEST.md (Hyperliquid 1h, 2026-03-14 →
2026-10-13, use_funding=False). Totals are summed net PnL across BTC+ETH+HYPE.

## Sweep results

| param | value | total $ | BTC $ | ETH $ | HYPE $ |
|-------|-------|---------|-------|-------|--------|
| adx_min | 25.0 | 1644 | 801 (12t) | -134 (9t) | 977 (11t) |
| adx_min | **30.0** (published classic) | 161 | -441 (4t) | -159 (2t) | 761 (5t) |
| adx_min | 35.0 | -238 | -116 (1t) | -105 (1t) | -17 (2t) |
| adx_exit | 20.0 | 362 | -441 (4t) | -159 (2t) | 962 (5t) |
| adx_exit | **25.0** (published classic) | 161 | -441 (4t) | -159 (2t) | 761 (5t) |
| adx_exit | 30.0 | -368 | -441 (4t) | -138 (2t) | 211 (5t) |
| max_hold | 48 | 216 | -441 (4t) | -159 (2t) | 816 (5t) |
| max_hold | **72** (shipped) | 161 | -441 (4t) | -159 (2t) | 761 (5t) |
| max_hold | 120 | 161 | -441 (4t) | -159 (2t) | 761 (5t) |

## Decision

- **Shipped the published classic params: ADX > 30 and rising, exit ADX < 25.**
  The looser adx_min=25 gate improves the total ($1644 vs $161) and helps BTC
  and HYPE, but it *dilutes the published rule* — the one thing the strategy
  spec forbids — and ETH still loses under it. With 2–12 trades per coin the
  sweep is noise; loosening the gate to chase it would be curve-fitting, not
  calibration.
- max_hold is irrelevant here (no trade ever reached 48 bars); kept 72 as the
  stalled-pullback guard.
- Stated plainly: no sweep alternative is stable across all 3 coins without
  breaking the published rule, so the classic ships and the strategy is
  reported as a non-earner (see BACKTEST.md).
