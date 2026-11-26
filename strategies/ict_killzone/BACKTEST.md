# ICT Killzone — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, read from the
local cache only (`data/candles/{BTC,ETH,HYPE}_1h.csv`), pinned
batch-47 window ms `[1773525600000, 1795701600000)`
(2026-03-14 22:00 UTC → 2026-11-26 14:00 UTC exclusive, last
bar 13:00 UTC): 6,160 bars BTC/ETH, 6,158 HYPE (HYPE's first
bar is 2026-03-15 00:00 UTC). Funding not modeled (fully
offline run).
**Costs:** 0.045% taker fee + 0.01% slippage per side.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start per coin. WARMUP=50 bars.

## Results (shipped config: Asian-range sweep in the London
07:00-10:00 UTC or NY 12:00-14:00 UTC killzone, >=1.0x ATR
displacement breaking the near swing, entry on a cross of
the 50% level of the displacement leg; 2xATR stop, 3xATR
trail, 24-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 1 | 100.0% | +$4 | +0.0% | +0.05 | -0.7% | +$4.49 | inf |
| ETH | 1 | 100.0% | +$5 | +0.1% | +0.13 | -0.2% | +$5.35 | inf |
| HYPE | 0 | — | $0 | 0.0% | 0.00 | 0.0% | $0.00 | 0.00 |
| **Combined** | **2** | **100.0%** | **+$10** | — | **+0.10** | **-0.3%** | **+$4.92** | **inf** |

Fees: BTC $9.44, ETH $6.23, HYPE $0.00 (total $15.68).
Net % is the final-equity return (it includes the
mark-to-market of any position still open at the window end);
Net $ is the sum of closed-trade PnL.

## Verdict: two trades in eight months -- the killzone chain almost never completes

Combined +$10 on 2 trades (both exited on max hold, both
nominal winners of ~$5) is not a result, it is a rounding
error with a 100% win rate attached. The mechanics do fire:
setups armed on 72 bars across the three coins (BTC 30,
ETH 19, HYPE 23 armed bars), but only 2 of those armed
setups ever saw the close cross the 50% level before the
day ended -- after a >= 1.0x ATR displacement, price
usually does not retrace halfway the same day, and the
day-boundary expiry kills the rest. HYPE armed 23 bars and
entered zero times. Honest read: the killzone entry as
specified (full sweep -> displacement -> 50% retracement,
same UTC day, on 1h bars) is too rare to evaluate, let alone
trade. The 100% win rate means nothing on n=2.

## Mechanism

State machine per side, gated to the killzone windows
(London 07:00-10:00 UTC, NY 12:00-14:00 UTC, end-hour bar
inclusive -- see the deviation note in README.md): a close
beyond the Asian high/low (00:00-03:00 UTC range of the
current UTC day), back inside within 2 bars of the sweep-
extreme bar, then within the same window a move of >= 1.0x
ATR(14) from the back-inside close that also breaks the near
swing (frozen at the back-inside bar). The leg runs from the
sweep extreme to the displacement extreme; entry is a close
crossing the 50% level of the leg (the FVG-midpoint
approximation). A pending setup is cancelled by a close
beyond the leg start and expires at the UTC day boundary.
The house 2xATR stop / 3xATR trail sit behind the signal
exit, with a 24-bar max hold enforcing the intraday design.

Sources: ICT kill zones --
https://www.ictkillzone.com/ict-kill-zones and
https://audacity.capital/trading-guides/ict-kill-zones/

## Limitations

- Two trades total: no per-coin read generalises, and the
  combined +$10 is meaningless as evidence.
- Both trades exited on max hold, not on the signal exit,
  so the backtest says nothing about whether killzone exits work.
- The day-boundary expiry is doing most of the work: 70 of
  72 armed bars expired without an entry.
- Single ~8.4-month crypto window; funding unmodeled;
  next-bar-open execution vs idealized entry.
- Never tune the shipped displacement threshold on this window.
