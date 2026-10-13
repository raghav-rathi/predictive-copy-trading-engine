# jhadchiti trend (55-bar breakout) — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars,
2026-03-14 22:00 UTC → 2026-10-10 13:00 UTC (BTC/ETH 5037 bars, HYPE 5035 bars).
Funding: full-window hourly `fundingHistory` per coin, paged from the public
endpoint and cached in `funding_{BTC,ETH,HYPE}.csv` (|rate| <= 0.00025/hr =
20bps/8h gate). **Costs:** 0.045% taker fee + 0.01% slippage per side.
Funding *accrual* not modeled in PnL (gate only).
**Sizing:** 0.75% equity risk per trade (author's sizing) on the 2xATR(20)
stop, 3x leverage cap, $10k start. Warmup 230 bars.

## Results (shipped config: 55-bar close breakout, BTC SMA(200) regime, funding gate, 30-bar coin-vs-BTC momentum, 2xATR(20) stop, 2160-bar max hold)

| Coin | Trades (signals) | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 0 (0) | — | $0.00 | 0.0% | 0.00 | 0.0% | — | — |
| ETH | 64 (267) | 23.4% | +$556.36 | +5.6% | +0.53 | -13.8% | +$8.69 | 1.15 |
| HYPE | 55 (292) | 27.3% | -$1,267.53 | -12.7% | -1.84 | -14.5% | -$23.05 | 0.52 |
| **Combined** | **119** | **25.2%** | **-$711.16** | — | — | — | **-$5.98** | — |

**BTC trades zero by construction:** the momentum filter compares the coin's
30-bar return against BTC's 30-bar return, so BTC-vs-BTC can never qualify.
BTC is the benchmark, not a candidate — the honest adaptation of the
author's top-20%-vs-BTC universe filter to a 3-coin universe. Documented,
not a bug.

## Verdict: MIXED — ETH works, HYPE doesn't, BTC ineligible

ETH is the only winner of the day's four strategies: 23.4% win rate with
avg win $289.56 vs avg loss $77.29 (3.75x payoff skew) — exactly the
positively-skewed trend profile the author describes (~30% win rate).
43 longs / 21 shorts; 44 exits on the 2xATR stop, 20 on the 20-period
channel cross. HYPE loses on the same rules (payoff skew only 1.39x —
breakouts on HYPE chop into the stop). Combined −$711: not a system to
size up yet, but ETH's skew is the one genuine edge in this batch.

## Mechanism

Long when ALL hold: (a) close > highest close of last 55 bars; (b) BTC
SMA(200) on 1h rising vs its value 20 bars ago — 1h adaptation of the
author's daily-frame regime rule; (c) |hourly funding| <= 0.00025
(20bps/8h, "not dangerously crowded"); (d) coin 30-bar return > BTC 30-bar
return — adaptation of the author's top-20%-vs-BTC universe filter to our
3-coin universe. Shorts mirror (regime inverted, coin underperforms BTC).
Exit on close crossing the 20-period close channel against the position,
2xATR(20) stop, or 2160-bar (90-day) max hold. 0.75% risk per trade.
