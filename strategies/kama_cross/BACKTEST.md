# KAMA Cross — Backtest

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

## Results (shipped config: fast KAMA(ER 10, fast 2, slow 30)
vs slow KAMA(ER 20, fast 2, slow 30), long on the fast
crossing above the slow, short on crossing below, exit on the
opposite cross, 2xATR stop, 3xATR trail, 60-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 232 | 31.0% | -$3,319 | -32.4% | -2.26 | -40.3% | -$14.30 | 0.67 |
| ETH | 224 | 40.6% | +$228 | +4.0% | +0.35 | -23.3% | +$1.02 | 1.02 |
| HYPE | 240 | 35.8% | +$1,788 | +16.8% | +1.00 | -19.6% | +$7.45 | 1.13 |
| **Combined** | **696** | **35.8%** | **-$1,302** | — | **-0.24** | **-16.6%** | **-$1.87** | **0.96** |

Fees: BTC $2,000, ETH $1,936, HYPE $1,349 (total $5,285).
Net % is the final-equity return (it includes the
mark-to-market of any position still open at the window end);
Net $ is the sum of closed-trade PnL.

## Verdict: a small loser overall — the adaptive cross works
on HYPE and ETH and fails on BTC

Combined -$1,302 on 696 trades, PF 0.96 — essentially
breakeven before the BTC leg drags it under. The coin split
is the story: HYPE +$1,788 (Sharpe +1.00, PF 1.13) and ETH
+$228 (PF 1.02) are both positive, while BTC -$3,319
(Sharpe -2.26, MaxDD -40.3%, PF 0.67) loses more than the
other two make. Exits are dominated by the hard stop (169 /
153 / 162 stop exits vs 59 / 65 / 70 signal exits): the cross
is slow to confirm, so by the time it flips the 2xATR stop
has usually already taken the trade out. Win rates 31–41%
with PF near 1.0 say the edge, if any, is thin: the KAMA
adapts to noise as designed, but on 1h crypto the fast/slow
ER gap (10 vs 20 bars) does not separate trend from chop
reliably enough to pay for 696 round trips at $5,285 in
fees. Honest read: not a winner, not a disaster — a
coin-dependent marginal system whose BTC leg is a genuine
loser.

## Mechanism

Perry Kaufman, "Smarter Trading" (1995): ER_t = |C_t −
C_{t−n}| / sum of |daily changes| over n bars; SC_t = (ER_t
× (2/3 − 2/31) + 2/31)^2; KAMA_t = KAMA_{t−1} + SC_t × (C_t
− KAMA_{t−1}), seeded at the first close. Two KAMAs share
fast 2 / slow 30 smoothing and differ only in the ER window
(10 fast, 20 slow). Long when the fast KAMA crosses above
the slow KAMA; short when it crosses below; exit on the
opposite cross. The harness 2xATR hard stop / 3xATR
chandelier trail sit behind the cross as a safety net for
gap-through-cross moves; 60-bar max hold.

Source: Perry Kaufman, "Smarter Trading" (1995) — KAMA —
https://docs.wickra.org/Indicators/Indicator-Kama (URL as
given in the batch-46 brief).

## Limitations

- Single ~8.4-month crypto window; the verdict is
  coin-dependent (HYPE/ETH positive, BTC deeply negative),
  so no single-coin read generalises.
- The cross lags: stop exits outnumber signal exits ~2.5:1,
  so most trades are decided by the harness stop, not the
  KAMA logic.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped ER periods on this window.
