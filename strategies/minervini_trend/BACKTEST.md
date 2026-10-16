# Minervini Trend Template — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → 2026-10-15
(BTC 5,157 bars; ETH 5,157; HYPE 5,155).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.
**Warmup:** 4,900 bars (the 200d SMA + 30d rising check need the history).

## Results (shipped config: full 8-criterion template, stage-2 entry on the
false→true flip, exit on template breakdown, 2xATR stop, 3xATR trail,
720-bar max hold, LONG ONLY)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 0 | — | $0 | 0.0% | 0.00 | 0.0% | — | — |
| ETH | 0 | — | $0 | 0.0% | 0.00 | 0.0% | — | — |
| HYPE | 7 | 0.0% | −$514 | −5.1% | −2.94 | −5.3% | −$73.36 | 0.00 |
| **Combined** | **7** | **0.0%** | **−$514** | — | — | — | **−$73.36** | — |

## Verdict: untestable on this data — 7 trades total, 0 on the majors

The template needs a 200-day SMA plus a 30-day rising comparison, which
forces a 4,900-bar warmup on ~5,157 bars of history — leaving roughly 258
tradeable bars (about 11 days). BTC and ETH never produced a single
stage-2 entry in that window; HYPE produced 7, all losers. That is not a
verdict on Minervini's template — it is a verdict on the sample size.
The 52wk high/low windows (12,480 bars) also exceed the available history
and fall back to all-available-history with min_periods=1 (documented in
the indicators module). This strategy needs multi-year daily data to be
judged; on hourly crypto history it is a research scaffold, not a signal.

## Implementation notes (rules in my own words)

- 1 day = 24 bars. Template terms: price above SMA(150d) and SMA(200d);
  SMA(150d) above SMA(200d); SMA(200d) rising versus 30 days ago;
  SMA(50d) above both longer MAs; price above SMA(50d); price at least
  30% above the 52wk low; price within 25% of the 52wk high.
- The published template's relative-strength-rating criterion is omitted
  (it requires a market benchmark series, which the harness does not
  carry) — documented, not silently dropped.
- LONG ONLY: Minervini's method does not short; `allow_shorts=False`.
