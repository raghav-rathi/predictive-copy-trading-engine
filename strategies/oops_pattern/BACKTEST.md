# Oops Gap Reversion — Backtest

**Data:** local Hyperliquid 1h cache CSVs
(`data/candles/{BTC,ETH,HYPE}_1h.csv`), sliced to the batch window
2026-03-14 00:00 UTC → 2026-10-22 00:00 UTC
(ms `[1773446400000, 1792627199000)`; actual data starts 2026-03-14
22:00 UTC for BTC/ETH, 2026-03-15 00:00 UTC for HYPE): 5,301 bars
BTC/ETH, 5,299 HYPE. Fully offline — no API calls.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 1.5xATR stop, 3x leverage
cap, $10k start. WARMUP=48 bars.

## Results (shipped config: session=24, long on the first close back
above the gap bar's pinned prior-session low within 24 bars of a
gap_down; short mirror; exits on the opposite Oops signal,
1.5xATR stop, 24-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 175 | 33.1% | -$3,501 | -35.0% | -2.42 | -37.6% | -$20.01 | 0.67 |
| ETH | 166 | 39.2% | +$25 | +0.3% | +0.15 | -23.4% | +$0.15 | 1.00 |
| HYPE | 185 | 43.2% | +$6,652 | +66.5% | +2.80 | -9.9% | +$35.96 | 1.48 |
| **Combined** | **526** | **38.6%** | **+$3,176** | — | — | — | +$6.04 | — |

## Verdict: a loser wearing a HYPE costume

Combined +$3,176 across 526 trades, and every dollar of it is HYPE:
+$6,652 with Sharpe +2.80, PF 1.48, expectancy +$35.96, and a shallow
-9.9% max drawdown. The pinned-reclaim rule catches HYPE's 2026
breakdown-and-snapback sequences well — 185 trades is a sensible pace
for a gap pattern, and fees ($1,534) are a manageable 23% of gross.

Everything else is red ink:

- **BTC is a blowout loser** (-$3,501, PF 0.67, Sharpe -2.42,
  MaxDD -37.6% — over a third of the account gone). On BTC, the
  "overreaction" that gaps below the prior session's low usually
  keeps going: fading the breakdown gets run over.
- **ETH is exactly zero** (+$25, PF 1.00, expectancy +$0.15,
  Sharpe +0.15). Fees ($1,854) are 74x the net. A coin flip with
  extra steps.
- 526 trades in one 7-month regime is a thin sample, and the combined
  green depends entirely on HYPE behaving like HYPE — the same
  single-coin-carries-everything shape as batch 12's trix.

Treat this as a HYPE-specific gap-fade filter with paper evidence,
not a three-coin strategy. The honest read: the Oops adaptation only
works where breakdowns reliably snap back, and in this window that
was HYPE alone.

## Calibration note

Shipped the specified session=24. A 12/24/48 session sweep is in
CALIBRATION.md: session=24 is the in-sample combined winner
(+$3,176); session=12 is negative combined (-$5,346) and session=48
is negative combined (-$3,931), with session=48 the only setting
where HYPE itself goes red (-$1,161). The session=24 setting was fixed
a priori — adopted before the sweep, not because of it.

## Mechanism

24-bar session proxies a trading day on 1h. prev_day_low/high =
completed prior session's min(low)/max(high) (rolling(24).min/max
shifted 24 — no lookahead). gap_down = open < prev_day_low,
gap_up = open > prev_day_high. Long = first close back above the gap
bar's pinned prev_day_low within 24 bars of the gap (one entry per
gap; expires otherwise); short = mirror. Exits = opposite Oops
signal or the 24-bar max hold (flat by session end). 1.5xATR stop,
no trail/target.

Source: Oops Pattern (Larry Williams) —
https://tr.tradingview.com/chart/AMZN/jING0osQ-The-OOPS-Pattern/

## Limitations

- Single 7-month crypto window; 526 trades is a thin sample, and all
  of the green is HYPE.
- BTC leg is deeply negative (-35%); ETH leg is pure noise.
- Crypto has no true opens: "gaps" are breakdown/breakout opens on
  1h bars, rarer and structurally different from equity opening gaps.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped session on this window (see CALIBRATION.md).
