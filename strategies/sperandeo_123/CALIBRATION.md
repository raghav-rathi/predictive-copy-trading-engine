# 1-2-3 Trend Change (Sperandeo) — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-14 → 2026-10-18, same costs/sizing). One variant against the
shipped config: wider risk — stop 2.0xATR / target 4.0xATR instead of
1.5/3.0 (still a 2R ratio, looser point-2 proxy). Sweep script:
`/tmp/bt_batch9.py` (`sperandeo_123 cal` mode).

| Variant | Coin | Trades | Win% | Net $ | Sharpe | PF |
|---|---|---|---|---|---|---|
| shipped 1.5/3.0 | BTC | 40 | 30.0% | -$948 | -1.40 | 0.68 |
| shipped 1.5/3.0 | ETH | 32 | 40.6% | +$296 | +0.51 | 1.14 |
| shipped 1.5/3.0 | HYPE | 38 | 34.2% | -$121 | -0.11 | 0.95 |
| wider 2.0/4.0 | BTC | 38 | 31.6% | -$601 | -0.86 | 0.77 |
| wider 2.0/4.0 | ETH | 32 | 40.6% | +$204 | +0.38 | 1.10 |
| wider 2.0/4.0 | HYPE | 38 | 36.8% | +$269 | +0.46 | 1.11 |

## One-line verdict

- **Wider stop/target (2.0/4.0):** loses less everywhere that matters —
  combined -$128 vs -$773 shipped, BTC's loss shrinks by a third, HYPE
  flips to a small win. The wider stop survives more of the post-entry
  chop that the 1.5xATR stop was donating to. But it does not create
  edge: BTC still loses, expectancy stays near zero, and the ranking of
  coins is unchanged.
- **Shipped decision:** keep the specified 1.5xATR stop / 3.0xATR target
  as the registry config. The variant's improvement is "less bad", not
  "good", and tuning risk multiples on 110 in-sample trades is not a
  basis for adopting a new config.
