# ICT Optimal Trade Entry (OTE) — Backtest

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

## Results (shipped config: 20-bar swing sweep, >=1.5x ATR
displacement breaking the near swing, entry on retracement
into the 62-79% OTE zone; invalidation beyond 100% of the
leg, 24-bar setup expiry; 2xATR stop, 3xATR trail, 120-bar
max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 1 | 0.0% | -$114 | -1.1% | -1.45 | -1.1% | -$113.88 | 0.00 |
| ETH | 2 | 50.0% | +$113 | +1.1% | +0.56 | -1.7% | +$56.50 | 3.58 |
| HYPE | 5 | 60.0% | +$367 | +3.7% | +1.21 | -3.1% | +$73.37 | 2.86 |
| **Combined** | **8** | **50.0%** | **+$366** | — | **+0.96** | **-1.2%** | **+$45.75** | **2.03** |

Fees: BTC $32.96, ETH $19.67, HYPE $23.88 (total $76.50).
Net % is the final-equity return (it includes the
mark-to-market of any position still open at the window end);
Net $ is the sum of closed-trade PnL.

## Verdict: nominally positive, statistically nothing -- eight trades in eight months

Combined +$366 on 8 trades (PF 2.03, Sharpe +0.96) is a
win by $366 and a rounding error by any other measure: one
trade per coin-month, so a single stop-out swings the whole
verdict. Every trade exited on the stop (8/8 stop exits, 0
signal exits) -- the 2xATR stop, not the OTE logic, decided
every trade; the signal exit (close beyond the sweep
extreme) never fired once. HYPE (+$367, 3W-2L) is the whole
combined profit; ETH is +$113 on two coin flips; BTC lost
its only trade. Honest read: the full sweep -> displacement
-> retracement chain almost never completes on 1h crypto
bars, and the eight completions carry no evidence the zone
itself has edge. Do not trade on this.

## Mechanism

State machine per side: a close beyond the prior 20-bar
swing extreme, back inside within 3 bars of the sweep-
extreme bar, then within 6 bars a move of >= 1.5x ATR(14)
from the back-inside close that also breaks the near swing
(frozen at the back-inside bar). The leg runs from the sweep
extreme to the displacement extreme; the OTE zone is 62-79%
retracement of that leg (70.5% midline diagnostic). Entry on
a close inside the zone; the setup is consumed on entry,
cancelled by a close beyond 100% of the leg, or expired 24
bars after the displacement extreme. The house 2xATR stop
replaces ICT's structural stop beyond the leg start (the
leg start is still the signal exit and the invalidation).

Sources: ICT Optimal Trade Entry --
https://tradingdocs.vercel.app/en/ict/ote and
https://orderblock.net/ict/optimal-trade-entry

## Limitations

- Eight trades total: no per-coin read generalises, and the
  combined +$366 is one trade away from negative.
- All exits were stops: the signal exit never fired, so the
  backtest says nothing about whether OTE exits work.
- Single ~8.4-month crypto window; funding unmodeled;
  next-bar-open execution vs idealized entry.
- Never tune the shipped displacement threshold on this window.
