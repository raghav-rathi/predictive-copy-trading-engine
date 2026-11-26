# RSI + Session VWAP — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, read from the
local cache only (`data/candles/{BTC,ETH,HYPE}_1h.csv`), pinned
batch-47 window ms `[1773525600000, 1795701600000)`
(2026-03-14 22:00 UTC → 2026-11-26 14:00 UTC exclusive, last
bar 13:00 UTC): 6,160 bars BTC/ETH, 6,158 HYPE (HYPE's first
bar is 2026-03-15 00:00 UTC). Funding not modeled (fully
offline run).
**Costs:** 0.045% taker fee + 0.01% slippage per side.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start per coin. WARMUP=40 bars.

## Results (shipped config: RSI(14) cross through 30/70 with
the close on the VWAP side -- long above session VWAP, short
below; exit on RSI crossing 50 against the position or the
close crossing the session VWAP against the position; 2xATR
stop, 3xATR trail, 120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 51 | 25.5% | -$642 | -6.4% | -1.26 | -9.1% | -$12.58 | 0.60 |
| ETH | 41 | 24.4% | -$343 | -3.4% | -0.71 | -8.2% | -$8.36 | 0.70 |
| HYPE | 36 | 27.8% | +$638 | +6.4% | +1.33 | -6.4% | +$17.71 | 1.53 |
| **Combined** | **128** | **25.8%** | **-$347** | — | **-0.32** | **-7.5%** | **-$2.71** | **0.91** |

Fees: BTC $479.98, ETH $276.45, HYPE $161.00 (total $917.43).
Net % is the final-equity return (it includes the
mark-to-market of any position still open at the window end);
Net $ is the sum of closed-trade PnL.

## Verdict: a loser -- the RSI-30/70 cross against VWAP buys the dip into a downtrend

Combined -$347 on 128 trades (PF 0.91, Sharpe -0.32) is a
small loss with a clear pattern: win rates 24-28% on all
three coins, so the system is right about one time in four
and the winners do not pay for the losers except on HYPE.
Signal exits dominate (111 / 128): the RSI-50 / VWAP-cross
exit fires quickly, so trades are cut short before any
trend can develop -- the entry is a counter-trend bounce
(RSI crossing up from oversold) but the exit is a
trend-following one (RSI back below 50), and the two do not
fit together on 1h bars. BTC (-$642, Sharpe -1.26, PF 0.60)
is the worst; ETH (-$343) agrees; HYPE (+$638, Sharpe
+1.33, PF 1.53) is the lone dissent and is not enough to
carry the other two. Honest read: no edge here -- the
combination loses on two of three coins and the combined
read is negative after $917 of fees.

## Mechanism

Session VWAP anchored at each UTC-day boundary (00:00 UTC):
VWAP = cumulative sum(tp * v) / sum(v) since the session
start, tp = (h + l + c) / 3, resetting each UTC day -- the
exact construction of `vwap_session_breakout`. Long when
RSI(14) crosses up through 30 while the close is above the
session VWAP; short when RSI(14) crosses down through 70
while the close is below it. Exit when RSI crosses 50
against the position or the close crosses the session VWAP
against the position. The harness 2xATR hard stop / 3xATR
chandelier trail sit behind the signal exits; 120-bar max
hold.

Source: RSI + session VWAP (standard combination;
session-VWAP convention per `vwap_session_breakout`) --
https://en.wikipedia.org/wiki/Relative_strength_index

## Limitations

- Single ~8.4-month crypto window; the verdict is
  coin-dependent (HYPE positive, BTC/ETH negative), so no
  single-coin read generalises.
- The RSI-50 exit fires fast (signal exits 111/128), so
  most trades are decided by the exit logic, not the stop.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped RSI levels on this window.
