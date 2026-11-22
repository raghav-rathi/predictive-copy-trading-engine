# Multi-Timeframe EMA Agreement — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`), pinned window
2026-03-14 22:00 UTC → 2026-11-21 14:00 UTC: BTC/ETH 6,040 bars,
HYPE 6,038 bars.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=120 bars.

## Results (shipped config: 1h EMA(9)/EMA(21) cross gated on 4h
EMA(9) > EMA(21) agreement, opposite-cross exit, 2xATR stop,
3xATR trail, 120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 99 | 27.3% | -$1,100 | -11.0% | -0.85 | -21.1% | -$11.11 | 0.77 |
| ETH | 112 | 25.0% | +$316 | +3.2% | +0.33 | -22.2% | +$2.83 | 1.06 |
| HYPE | 95 | 32.6% | +$1,849 | +18.5% | +1.44 | -10.0% | +$19.46 | 1.37 |
| **Combined** | **306** | **28.1%** | **+$1,065** | — | — | — | **+$3.48** | — |

Fees: BTC $1,096, ETH $1,039, HYPE $548 (total $2,683).

## Verdict: mixed, and the per-coin split is the story

306 trades is a real sample, and the combined +$1,065 (+10.7%
on $10k) is positive — but it is carried entirely by HYPE
(+$1,849), while BTC lost −$1,100 with a −21.1% drawdown and
ETH is flat (+$316, Sharpe +0.33). The same filter, the same
window, three different signs. That is not a clean confirmation
of the BotLab result:

- The win rate is low everywhere (25–33%): this is a
  trend-following cross with a wide trail, so it lives or dies
  on a few large winners. BTC's losers outran its winners
  (PF 0.77); HYPE's did not (PF 1.37).
- Drawdowns are large (−21% BTC, −22% ETH) for a strategy
  risking 1% per trade — the 3xATR trail lets adverse trends
  run, and the 120-bar max hold keeps losers in the book.
  The combined number hides this: no single-coin run here is
  something to size up on.
- The study's surviving result was on a 4h mean-reversion bot's
  ledger, not on a 1h EMA-cross base, and the authors warn
  explicitly that it is "a reason to keep testing..., not a
  reason to trade it." This run is consistent with that caution:
  suggestive on HYPE, negative on BTC, inconclusive overall.

## Mechanism

1h EMA(9)/EMA(21) cross, taken only when the 4h EMA(9)/EMA(21)
pair (computed from completed 4h bars only) agrees with the
trade direction; exit on the opposite 1h cross. 2xATR stop,
3xATR trail, 120-bar max hold. All params fixed a priori; no
optimization.

Source: BotLab — "Do Funding Rate and Open Interest Filters
Improve a Crypto Bot?"
(https://botlab.org.uk/learn/do-funding-rate-and-open-interest-filters-improve-a-crypto-bot).

## Limitations

- Single 8-month crypto window; funding unmodeled (the study
  included funding — its absence here flatters shorts slightly
  in high-funding regimes); next-bar-open execution vs
  idealized entry.
- The 4h filter's agreement rate was not measured here: if it
  agrees with ~95% of crosses it is doing little work, and the
  per-coin divergence suggests the base cross, not the filter,
  is driving most of the P&L.
- Never tune the shipped parameters on this window.
