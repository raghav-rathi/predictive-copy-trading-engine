# Elder Impulse System — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → 2026-10-18
(~5,224 bars each). Note: the batch brief's ms window constants were stamped
2025 (they filtered to an empty frame against 2026 data); corrected by +365d
to the intended 2026 window. Cache rows deduplicated in-memory (5 identical
overlap rows per file from cache-extension appends; cache files untouched).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 1.5xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: EMA13 + MACD(12,26,9) histogram impulse color, long on green / short on red / flat on flip, 1.5xATR stop, 48-bar max hold, WARMUP=60)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 1,174 | 24.5% | -$9,511 | -95.1% | -11.30 | -95.2% | -$8.10 | 0.47 |
| ETH | 1,185 | 22.7% | -$9,270 | -92.7% | -9.57 | -92.8% | -$7.82 | 0.51 |
| HYPE | 1,173 | 29.0% | -$8,263 | -82.5% | -7.61 | -82.7% | -$7.04 | 0.55 |
| **Combined** | **3,532** | **25.4%** | **-$27,044** | — | — | — | -$7.66 | — |

## Verdict: LOSER — do not trade

Loses on every coin, catastrophically: −83% to −95% of equity, profit
factors 0.47–0.55, Sharpe −7.6 to −11.3. The failure is structural, not
just costs. The spec's exit rule (long_exit on any non-green bar) means
positions live only while the impulse color holds; on 1h crypto the
EMA13/MACD-histogram pair flips every few bars, so the system takes
~1,175 trades per coin (≈1 trade every 4.4 bars) and each trade is a
coin-flip-or-worse stub with a 1.5xATR stop. Even gross of costs the book
is deeply negative (PF ≤ 0.55) — fees ($14.0k combined) only deepen a hole
the edge dug first. The impulse color is a fine *filter*; as a
trade-every-bar entry/exit engine it is churn.

## Calibration note

Shipped exactly the specified parameters (EMA13, MACD(12,26,9), green/red/
blue color, long-on-green/short-on-red, exit on flip, 1.5xATR stop, 48-bar
max hold, WARMUP=60). The one-variant sweep (EMA13 → EMA21, slower impulse)
is reported in CALIBRATION.md — it does not rescue the strategy on any
coin. No further tuning attempted: the failure mode (flip-churn) is
structural to the specified exit rule.

## Mechanism

Per bar: EMA13 of close; MACD histogram = MACD(12,26,9) line minus signal.
Bar is green when EMA13 rises AND histogram rises, red when both fall, blue
otherwise. Long on green, short on red; long exits when the bar is not
green (flip to blue or red), short exits when not red. 1.5xATR hard stop,
48-bar max hold, no trailing, no target.

Source: Alexander Elder, *Come Into My Trading Room* — Elder Impulse System —
https://chartschool.stockcharts.com/table-of-contents/chart-analysis/chart-types/elder-impulse-system.md

## Limitations

- Single 7-month crypto window (choppy-to-bearish); no bull-market sample.
- Funding unmodeled (short book would earn it; longs would pay).
- Next-bar-open execution vs idealized signal-bar entry.
- 1h bars only; Elder's system is natively multi-timeframe — the brief
  specified the single-frame color rule, which is what was tested.
