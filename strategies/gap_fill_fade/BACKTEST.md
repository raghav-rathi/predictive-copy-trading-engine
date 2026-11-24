# Gap Fill Fade — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), pinned batch-45 window: 2026-03-14 22:00 UTC →
2026-11-24 14:00 UTC (BTC 6,111 bars, ETH 6,111 bars, HYPE
6,109 bars — exactly the expected counts).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR(14) stop, 3x
leverage cap, $10k start, long/short. WARMUP=30 bars.

## Results (shipped config: fade a >= 0.5 ATR gap on the gap
bar, exit on the fill or the opposite gap, 2xATR(14) stop,
24-bar max hold, no trail, no target)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 9 | 33.33% | -$69.85 | -0.70% | -0.20 | -2.61% | -$7.76 | 0.85 |
| ETH | 7 | 28.57% | -$21.49 | -0.21% | -0.05 | -2.41% | -$3.07 | 0.94 |
| HYPE | 9 | 55.56% | +$62.19 | +0.62% | +0.29 | -1.89% | +$6.91 | 1.19 |
| **Combined** | **25** | **40.00%** | **-$29.16** | — | — | — | **-$1.17** | — |

Fees: BTC $76.13, ETH $42.37, HYPE $40.21 (total $158.71).
Gross PnL before fees: +$129.55 combined — the fills earn a
little before costs, and fees eat all of it plus $29.16.

Exit reasons: BTC 2 signal / 4 stop / 3 max-hold; ETH 2
signal / 3 stop / 2 max-hold; HYPE 5 signal / 3 stop / 1
max-hold. Sides roughly balanced (BTC 5 long / 4 short; ETH
4 / 3; HYPE 4 / 5). Median holds: BTC 17 bars, ETH 24 bars
(the max hold), HYPE 6 bars.

## Verdict: scratch — and a 25-trade sample proves nothing

Combined -$29.16 across 25 trades with a 40.00% win rate and
a -$1.17 expectancy is breakeven to the dollar. That is the
honest headline, but the real verdict is that 25 trades over
eight months cannot distinguish an edge from noise: one
trade either way swings the combined result by ~$30–$100.
Do not quote this as a winner, a loser, or an edge — quote
it as untested.

- The per-coin split (BTC -$69.85, ETH -$21.49, HYPE
  +$62.19) is exactly what noise looks like at this sample
  size, and the HYPE "win" is 5 winning fills out of 9
  trades.
- The exit mix is the mechanism story: only 9 of 25 trades
  exit on a fill. 10 hit the 2xATR stop (the gap keeps
  running the wrong way) and 6 expire at the 24-bar max hold
  (the fill never arrives within a day). Fading an hourly gap
  on 24/7 crypto is fading a move that already happened, not
  a session-break dislocation — and the fill rate shows it.
- Fees ($158.71) exceed the gross edge (+$129.55). Even if
  the gross edge were real, the cost drag at this trade
  frequency (one trade per coin per month) makes it
  untradable as built.

Stated plainly: gap-fill fading on 1h crypto barely trades,
and what little it trades is a scratch. The daily-equity
gap-fill literature does not transfer to hourly bars of a
market that never closes.

## Mechanism

LONG on a gap down >= 0.5 ATR(14) vs the prior close, SHORT
on a gap up; one fade per gap, fired on the gap bar itself.
Exit on the fill (close >= prev_close for longs, <= for
shorts) or the opposite gap. 2xATR(14) stop, 24-bar max hold,
no trail, no target. All params fixed a priori; no
optimization.

Source: Gap-fill mean reversion (Bulkowski, *Encyclopedia of
Chart Patterns*) (https://thepatternsite.com/GaugingGaps.html).

## Limitations

- Single 8-month crypto window; funding unmodeled;
  next-bar-open execution vs idealized entry.
- 25 trades is far too small a sample for any statistical
  claim — the combined -$29.16 is within one trade of zero.
- Never tune the shipped parameters on this window — least
  of all the 0.5 ATR gap threshold or the 24-bar max hold,
  which directly control how many (few) trades fire.
