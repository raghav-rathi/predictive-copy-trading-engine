# The Strat — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, read from the
local cache only (`data/candles/{BTC,ETH,HYPE}_1h.csv`), pinned
batch-47 window ms `[1773525600000, 1795701600000)`
(2026-03-14 22:00 UTC → 2026-11-26 14:00 UTC exclusive, last
bar 13:00 UTC): 6,160 bars BTC/ETH, 6,158 HYPE (HYPE's first
bar is 2026-03-15 00:00 UTC). Funding not modeled (fully
offline run).
**Costs:** 0.045% taker fee + 0.01% slippage per side.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start per coin. WARMUP=200 bars.

## Results (shipped config: 2-1-2 / 3-1-2 / 2-2 reversal and
2-1-2 continuation setups, FTFC-gated daily AND weekly;
opposite-setup exit; 2xATR stop, 3xATR trail, 120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 420 | 25.2% | -$5,592 | -55.9% | -6.47 | -57.0% | -$13.32 | 0.43 |
| ETH | 402 | 26.9% | -$2,605 | -26.0% | -2.01 | -32.8% | -$6.48 | 0.71 |
| HYPE | 339 | 33.9% | -$3,175 | -31.8% | -3.64 | -36.4% | -$9.37 | 0.57 |
| **Combined** | **1,161** | **28.3%** | **-$11,372** | — | **-5.21** | **-40.6%** | **-$9.80** | **0.57** |

Fees: BTC $3,153, ETH $2,712, HYPE $1,291 (total $7,156).
Net % is the final-equity return (it includes the
mark-to-market of any position still open at the window end);
Net $ is the sum of closed-trade PnL.

## Verdict: a clear loser on every coin — the setups fire constantly and lose

Combined -$11,372 on 1,161 trades (PF 0.57, Sharpe -5.21,
MaxDD -40.6%) is not a marginal miss: every coin loses by a
wide margin, BTC worst (-$5,592, Sharpe -6.47, MaxDD -57.0%,
PF 0.43). Win rates 25–34% with PF 0.43–0.71 say the setups
have no edge on 1h crypto bars — a 2-1-2 or 2-2 pattern on
hourly bars is mostly noise, and the opposite-setup exit
churns the book: signal exits outnumber stop exits ~4:1
(334 / 327 / 289 vs 86 / 75 / 50), so positions flip on
every counter-setup instead of riding anything. The FTFC gate
helps — the calibration sweep shows the ungated variant loses
more than twice as much — but gating a losing signal only
loses more slowly. Honest read: do not trade this on 1h
crypto; the Strat's edge, if it exists, lives on higher
time frames or with the trigger-break entry the close-based
adaptation cannot reproduce.

## Mechanism

Each bar is classified vs the prior bar: 1 = inside (h <=
prior h AND l >= prior l), 2U = breaks the prior high only,
2D = breaks the prior low only, 3 = breaks both. Setups:
2-1-2 reversal (2D,1,2U long / 2U,1,2D short), 3-1-2 reversal
(3,1,2U long / 3,1,2D short), 2-2 reversal (2D,2U long /
2U,2D short), 2-1-2 continuation (2U,1,2U long / 2D,1,2D
short). Entries require FTFC: the daily (24-bar block) and
weekly (168-bar block) directions both green for longs, both
red for shorts, where a block's direction is its last close
minus its first open and is applied only after the block
completes. The entry signal fires on the close of the trigger
bar (the final 2 bar); the harness enters at the next bar's
open — the close-based adaptation of the book's trigger-break
entry. A long exits on any short setup, a short on any long
setup (exit not FTFC-gated). The harness 2xATR stop / 3xATR
trail / 120-bar max hold sit behind the signal exit.

Source: Rob Smith — The Strat —
https://www.luxalgo.com/library/concept/the-strat/ and
https://www.smoothstrat.com/course.html (bar classification,
setup list, and FTFC concept per the task brief; the
close-based trigger adaptation is documented above).

## Limitations

- Single ~8.4-month crypto window; the verdict is negative on
  all three coins, so no coin-dependence caveat rescues it.
- The book's trigger-break entry (stop above/below the 2 bar)
  is replaced by a close-based signal + next-bar-open entry;
  the tested system is the adaptation, not the book's
  intraday execution.
- Signal exits dominate (~4:1 over stops), so most trades are
  decided by the next counter-setup, not by the stop/trail.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped FTFC gate on this window.
