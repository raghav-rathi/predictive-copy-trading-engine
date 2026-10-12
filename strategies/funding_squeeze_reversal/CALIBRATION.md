# Funding Squeeze Reversal — threshold-scale sweep calibration

Swept the funding-threshold scale (both thresholds multiplied by the
scale; the confidence intensity normalization scales with it, so the
mechanism is unchanged) over {1.0, 0.5, 0.25} on the same data/costs/
sizing as BACKTEST.md (HL 1h + real fundingHistory, BTC+ETH+HYPE,
2026-03-14 → 2026-10-10, 0.045%+0.01% costs, funding accrued, 1% risk,
$10k start). Monkeypatched module constants via a throwaway script
(`/tmp/fsr_sweep.py`, not committed); no strategy code changed.

| Scale | Total trades | Total net $ | BTC | ETH | HYPE |
|---|---|---|---|---|---|
| 1.0 (author) | 17 | **+$436** | 0t / $0 | 1t / +$52 (1 trade) | 16t / +$385, WR 68.8%, PF 2.08 |
| 0.5 | 35 | +$272 | 3t / −$250, WR 0% | 6t / +$179, WR 83%, PF 2.65 | 26t / +$344, WR 57.7%, PF 1.46 |
| 0.25 | 375 | **−$1,334** | 100t / −$1,921, WR 39%, PF 0.57 | 129t / −$191, PF 0.96 | 146t / +$777, WR 49%, PF 1.13 |

## Takeaway

Shipped the author's 1.0x scale — it is the only scale with a positive
combined book, and it is not on a knife edge: 0.5x is also positive in
total (+$272) but BTC goes 0W–3L there, i.e. loosening the threshold lets
in non-extreme funding prints that the fade cannot beat. At 0.25x the
system degrades into 375-trade churn (−$1,334, PF < 1 on BTC and ETH):
the confidence gate cannot rescue entries that aren't real extremes.
The honest read: this is an extremes-only strategy. On Hyperliquid only
HYPE's funding regime produces author-scale extremes; BTC/ETH sit out.
No per-coin threshold tuning — that would be fitting to 17 trades.
