# EMA Ribbon Expansion — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, read from the
local cache only (`data/candles/{BTC,ETH,HYPE}_1h.csv`), pinned
batch-46 window ms `[1773525600000, 1795615200000)`
(2026-03-14 22:00 UTC → 2026-11-25 14:00 UTC exclusive, last
bar 13:00 UTC): 6,136 bars BTC/ETH, 6,134 HYPE (HYPE's first
bar is 2026-03-15 00:00 UTC). Funding not modeled (fully
offline run).
**Costs:** 0.045% taker fee + 0.01% slippage per side.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start per coin. WARMUP=60 bars.

## Results (shipped config: EMA ribbon 8/13/21/34/55, compression
window 20, compression within last 3 bars, exit on EMA8 crossing
back through EMA13, 2xATR stop, 3xATR trail, 60-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 134 | 22.4% | -$2,358 | -23.6% | -2.59 | -28.4% | -$17.60 | 0.51 |
| ETH | 122 | 27.9% | +$667 | +6.7% | +0.59 | -14.5% | +$5.46 | 1.15 |
| HYPE | 108 | 26.9% | -$917 | -9.2% | -0.76 | -11.6% | -$8.49 | 0.80 |
| **Combined** | **364** | **25.5%** | **-$2,608** | — | — | — | -$7.17 | — |

Fees: BTC $1,269, ETH $1,016, HYPE $508 (total $2,792).
Net % is the final-equity return (it includes the
mark-to-market of any position still open at the window end);
Net $ is the sum of closed-trade PnL.

## Verdict: loser combined — the ribbon coils, then expands the wrong way

Combined -$2,608 on 364 trades. The mechanism is the problem,
not the market: full five-EMA alignment after compression is a
lagging confirmation — by the time all five EMAs line up, the
move that uncoiled the ribbon is mostly spent, and the EMA8 <
EMA13 exit is slow to admit it. Win rate 22.4–27.9% and profit
factor 0.51–0.80 on BTC and HYPE say the entries catch the tail
of moves and the exits give back the rest. ETH is the lone
positive coin (+$667, PF 1.15, Sharpe +0.59) — one coin out of
three does not save a system whose combined expectancy is
-$7.17/trade. BTC is the worst read (-$2,358, Sharpe -2.59,
MaxDD -28.4%): the ribbon aligns, BTC reverses, the 2xATR stop
takes the trade out 53 times.

## Calibration note

Shipped the specified compression window 20. A 10/20/40
compression-window sweep on this batch-46 window is in
CALIBRATION.md: 40 is less negative combined (-$1,622, 124
trades) but still negative on every coin, and 10 is far worse
(-$8,655, 695 trades). The 20 config was fixed before any
backtest was run; no in-sample adoption — the shipped config
stays 20 and the verdict stays: loser.

## Mechanism

EMAs 8/13/21/34/55 of close (causal `ewm`, `adjust=False`).
Ribbon width = (EMA8 − EMA55)/EMA55. Compression = |width|
equal to its 20-bar rolling minimum; comp_recent = compression
true within the last 3 bars. Long when aligned bullish and
comp_recent; short when aligned bearish and comp_recent. Exit
when EMA8 crosses back through EMA13. The harness 2xATR hard
stop / 3xATR chandelier trail sit behind the ribbon exit as a
safety net for gap-through moves; 60-bar max hold.

Source: Guppy Multiple Moving Average (Daryl Guppy),
ribbon-expansion variant —
https://capital.com/en-int/learn/technical-analysis/gmma-indicator
(verified via search 2026-11-25; the GMMA two-group construction
is the shipped `guppy_mma` reference — this strategy uses a
single five-EMA ribbon with a compression gate instead).

## Limitations

- Single ~8.4-month crypto window; 364 trades — the failure is
  consistent across BTC and HYPE, with ETH the only exception.
- Full five-EMA alignment is a lagging entry: the signal fires
  after the expansion, not at its start.
- The calibration sweep shows a wider compression window helps
  in-sample (40 → -$1,622 combined) — but adopting it would be
  in-sample selection, and it is still negative on every coin.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped compression window on this window.
