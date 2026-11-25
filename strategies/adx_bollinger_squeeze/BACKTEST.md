# ADX Bollinger Squeeze — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, read from the
local cache only (`data/candles/{BTC,ETH,HYPE}_1h.csv`), pinned
batch-46 window ms `[1773525600000, 1795615200000)`
(2026-03-14 22:00 UTC → 2026-11-25 14:00 UTC exclusive, last
bar 13:00 UTC): 6,136 bars BTC/ETH, 6,134 HYPE (HYPE's first
bar is 2026-03-15 00:00 UTC). Funding not modeled (fully
offline run).
**Costs:** 0.045% taker fee + 0.01% slippage per side.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start per coin. WARMUP=50 bars.

## Results (shipped config: BB(20, 2.0), squeeze = bandwidth
at its 20-bar minimum, long/short on a close outside the
band with ADX(14) > 20 within 3 bars of a squeeze, exit on
the close coming back inside the bands or ADX < 15, 2xATR
stop, 3xATR trail, 60-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 65 | 27.7% | +$63 | +0.6% | +0.14 | -8.4% | +$0.97 | 1.04 |
| ETH | 60 | 35.0% | +$820 | +8.2% | +1.38 | -3.0% | +$13.66 | 1.71 |
| HYPE | 69 | 29.0% | -$212 | -2.1% | -0.51 | -7.6% | -$3.08 | 0.87 |
| **Combined** | **194** | **30.4%** | **+$670** | — | **+0.59** | **-3.6%** | **+$3.46** | **1.15** |

Fees: BTC $690, ETH $526, HYPE $351 (total $1,567).
Net % is the final-equity return (it includes the
mark-to-market of any position still open at the window end);
Net $ is the sum of closed-trade PnL.

## Verdict: a small winner — selective, low-drawdown, and
honest about how little edge it has

Combined +$670 on 194 trades (PF 1.15, Sharpe +0.59,
combined MaxDD only -3.6%) — the best risk-adjusted read of
the three batch-46 strategies, and the cheapest to run
($1,567 in fees on 194 trades vs $5,285 on 696 for KAMA).
ETH carries it (+$820, Sharpe +1.38, PF 1.71, MaxDD -3.0%);
BTC is flat (+$63) and HYPE slightly negative (-$212, PF
0.87). Signal exits dominate (57 / 56 / 66 vs 8 / 4 / 3 stop
exits): the band/ADX exit does the work, and the 2xATR stop
is almost never reached — the system gets out on its own
terms. But the win rate is only 27–35% and the combined
+$670 is ~2.2% on $30k over 8.4 months: this is a marginal,
low-frequency system, not a money machine. The squeeze +
ADX filter successfully avoids the chop that kills the
other two strategies (194 trades vs 696 and 536), and that
selectivity is the whole edge. On this window it is a
winner; on a different window the same selectivity could
just as easily produce 194 trades and nothing.

## Mechanism

John Bollinger's Bandwidth squeeze: BB(20, 2.0), bandwidth =
(upper − lower) / mid; a squeeze is bandwidth at its 20-bar
minimum. A squeeze says volatility is unusually low and an
expansion is likely — it says nothing about direction, so
the trade takes the breakout side, confirmed by ADX(14) >
20 within 3 bars of the squeeze. Exit when the close
crosses back inside the bands or ADX falls below 15. The
harness 2xATR hard stop / 3xATR chandelier trail sit behind
the signal exit as a safety net for gap-through-band moves;
60-bar max hold.

Source: John Bollinger — Bollinger Bands / Bandwidth squeeze —
https://www.nasdaq.com/articles/rare-volatility-indicator-helps-spot-price-breakouts-2019-04-15
(verified via web search 2026-11-25; confirms Bandwidth =
(upper − lower) / mid and the squeeze as a low-Bandwidth
setup preceding an expansion).

## Limitations

- Single ~8.4-month crypto window; 194 trades is a small
  sample and the combined +$670 could be noise — ETH alone
  is +$820, so without ETH the system is flat-to-negative.
- Win rate 27–35% with PF 1.15: the edge rests on a few
  larger winners; a run of failed breakouts would erase it.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped ADX thresholds on this window.
