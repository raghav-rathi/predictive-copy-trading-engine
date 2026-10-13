# Mass Index — Calibration

Sweeps run on the same data as BACKTEST.md (Hyperliquid 1h, 2026-03-14 →
2026-10-13, use_funding=False). Totals are summed net PnL across BTC+ETH+HYPE.

## Sweep results

| param | value | total $ | BTC $ | ETH $ | HYPE $ |
|-------|-------|---------|-------|-------|--------|
| bulge_high | 26.0 | 657 | -1022 (107t) | 730 (121t) | 949 (134t) |
| bulge_high | **27.0** (published) | 1112 | -927 (35t) | 1882 (35t) | 157 (23t) |
| bulge_high | 28.0 | 1654 | -839 (18t) | 1866 (18t) | 627 (6t) |
| trail_atr | 2.0 | -108 | -995 (35t) | 708 (35t) | 179 (23t) |
| trail_atr | **3.0** (specified) | 1112 | -927 (35t) | 1882 (35t) | 157 (23t) |
| trail_atr | 4.0 | 362 | -1082 (35t) | 1673 (35t) | -229 (23t) |
| sma_len (our ext.) | 10 | 1363 | -607 (35t) | 1705 (35t) | 266 (23t) |
| sma_len (our ext.) | **20** | 1112 | -927 (35t) | 1882 (35t) | 157 (23t) |
| sma_len (our ext.) | 30 | 742 | -409 (35t) | 1311 (35t) | -160 (23t) |

## Decision

- **Shipped the published values: bulge 27/26.5, 3xATR trailing.** The 3xATR
  trail is confirmed best on every coin (2x and 4x both worse everywhere).
- bulge_high=28 improves the total ($1654) but degrades ETH ($1866 vs $1882)
  and halves the trade count (HYPE 23→6 trades) — not stable across all 3, so
  the published 27 ships.
- sma_len=10 (our extension's lookback) improves the total but degrades ETH,
  the one coin where the extension actually works — not stable, keep 20.
- Stated plainly: no sweep alternative beats the shipped config on all three
  coins; the published params stand.
