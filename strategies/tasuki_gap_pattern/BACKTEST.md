# Tasuki Gap Pattern — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`), requested window
2026-03-14 → 2026-10-28 (t >= 1773446400000 and
t <= 1793145600000), $10k start, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per
side, funding off. WARMUP=20 bars.

**Actual window used (as returned by the cache):** BTC/ETH
first candle 1773525600000 (2026-03-14 22:00 UTC), last candle
1793145600000 (2026-10-28 00:00 UTC) — the cache starts 22
hours after the requested window start, so the first 22 hours
are missing, not shifted. HYPE first candle 1773532800000
(2026-03-15 00:00 UTC), last 1793145600000. The cache also
contains 5 exact-duplicate bars per coin; those were dropped
(keep first) before running, so bar counts below are
deduplicated. Note: the cache was extended to the window end
during this batch's work (it previously ended 2026-10-27
13:00 UTC); the numbers below are on the final cache state.

**Method note:** the backtest ran through the same
`strategies/backtest.py` `run_backtest` harness and the
strategy's own RiskConfig as `scripts/run_strategy_backtest.py`,
but on the window-filtered, deduplicated cache read directly
— the script's `fetch_candles` path would extend the cache
past the window end and change the window, so it was not used.

**Adaptation disclosure:** the shipped rule uses the
continuous-market adaptation described in README.md /
CALIBRATION.md (third close between the first and second
candle's closes). Under the literal textbook rule (third
close inside the first-close-to-second-open gap) this
strategy records ZERO trades on all three coins in this
window — the gaps are sub-tick on 24/7 crypto. The numbers
below are for the adapted rule only.

## Results (shipped config: gap + two strong same-color
candles + counter-color candle opening inside the second
body and closing between the first and second closes,
5-bar trend filter, 2xATR stop, 2.5xATR trail, 120-bar max
hold)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 8 | 37.5% | -$95.82 | -0.39 | -3.4% | -$11.98 | 0.71 |
| ETH | 10 | 50.0% | +$113.63 | +0.40 | -3.3% | +$11.36 | 1.35 |
| HYPE | 24 | 37.5% | +$220.69 | +0.46 | -4.7% | +$9.20 | 1.21 |
| **Combined** | **42** | **40.5%** | **+$238.49** | +0.37 | -2.2% | **+$5.68** | 1.14 |

Fees: BTC $81.44, ETH $74.80, HYPE $106.55 (total $262.79).
Exits: 39 stop / 3 signal / 0 max-hold — the stop, not the
pattern exit, manages nearly every trade. Combined Sharpe /
MaxDD are computed on the summed $30k three-coin equity curve.

## Verdict: no demonstrated edge (mildly green, not a win)

+$238 across 42 trades on $30k starting capital is 0.8% over
seven months before any funding or slippage beyond the
modeled rates — noise, not an edge. HYPE carries the book
(+$221) while BTC loses; a continuation pattern that loses
on the most liquid coin and wins only via stops on the
least liquid one is not tradeable as shipped.

## Limitations

- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Cache starts 22 hours late (BTC/ETH) / 24 hours late
  (HYPE first bar) vs the requested window start.
- The adaptation is disclosed above; do not compare these
  numbers to a literal-rule tasuki without noting it.
- Never tune the shipped parameters on this window.
