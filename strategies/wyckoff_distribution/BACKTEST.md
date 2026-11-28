# Wyckoff Distribution — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, read from the
local cache only (`data/candles/{BTC,ETH,HYPE}_1h.csv`), pinned
batch-49 window ms `[1773525600000, 1795874400000)`
(2026-03-14 22:00 UTC → 2026-11-28 14:00 UTC exclusive, last
bar 13:00 UTC Nov 27): 6,185 bars BTC/ETH, 6,183 HYPE. Funding
not modeled (fully offline run).
**Costs:** 0.045% taker fee + 0.01% slippage per side.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start per coin. WARMUP=150 bars. SHORT ONLY.

## Results (shipped config: 120-bar range, >=5% advance gate,
UTAD = poke above the 120-bar high reclaimed within 3 bars;
SOW = wide down bar closing below the range midpoint within 48
bars of a UTAD; LPSY = first lower-high pullback within 24
bars of an SOW; entry on the UTAD-reclaim bar or an LPSY
bar; exit above utad_high or below the 1.0x range
projection; 2xATR stop, 3xATR trail, 120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor | Fees |
|---|---|---|---|---|---|---|---|---|---|
| BTC | 19 | 15.8% | -$471.94 | -4.7% | -1.08 | -6.1% | -$24.84 | 0.56 | $154.84 |
| ETH | 24 | 29.2% | -$667.77 | -6.7% | -1.30 | -11.2% | -$27.82 | 0.48 | $150.89 |
| HYPE | 47 | 29.8% | -$980.39 | -9.8% | -1.47 | -12.0% | -$20.86 | 0.50 | $196.30 |
| **Combined** | **90** | **26.7%** | **-$2,120.11** | **-7.1%** | **-1.92** | **-8.7%** | **-$23.56** | **0.51** | **$502.03** |

Exit-reason breakdown: BTC stop 12 / signal 7; ETH stop 19 /
signal 5; HYPE stop 33 / signal 14. Net % is the final-equity
return ($30k combined -> $27,879.89); Net $ is the sum of
closed-trade PnL.

## Verdict: the mirror loses the same way the original did

Combined -$2,120 on 90 trades (win rate 26.7%, PF 0.51) is
a loser, and the failure mode is the accumulation mirror's
failure mode with the sign flipped: the structure detects
real events (BTC 24 UTADs / 1 SOW / 1 LPSY, ETH 26 / 5 / 5,
HYPE 58 / 6 / 6 -- the chain is rare, as a schematic should
be) and then 64 of 90 trades exit on the 2xATR hard stop,
only 26 on the signal exit. The UTAD high is usually only
just above the entry, so the "invalidation" and the hard
stop sit almost on top of each other and the trade has no
room to breathe: the UTAD reclaims, price chops, and the
stop (or a close back above utad_high) takes it out before
any markdown develops. BTC barely completes the chain at
all -- 1 SOW and 1 LPSY in the whole 8.4-month window, so 24
of its 25 entries are raw UTAD reclaims. HYPE trades twice
as often as BTC/ETH -- its noisier 1h tape throws far more
UTADs -- and still loses. The range projection exit almost
never pays: only 26 signal exits across all coins, and the
winners inside them do not cover 64 stops. Unlike the ORB
fade in this same batch, distribution loses even before
fees (gross -$1,618 on 90 trades); fees (-$502) are a
quarter of the damage, not the story. Honest read: on 1h
crypto the UTAD is a real pattern with a real failure mode
(the reclaim does not stick), and the 2xATR stop is too
tight for a 120-bar-hold schematic. Widening the stop would
be tuning on this window, so it stays as specified.

## Mechanism

State machine in indicators.py: the trailing 120-bar range
and a 5%-over-120-bars advance gate; a poke above the prior
range high that reclaims within 3 bars confirms a UTAD
(utad_high = highest high of the poke); within 48 bars a wide
down bar closing below the range midpoint with volume
confirmation is the SOW; within 24 bars the first bar
holding below utad_high with a close below range_high is
the LPSY. signals.py enters short on a UTAD-reclaim bar or
an LPSY bar, and exits on a close above the entry-frozen
utad_high or below the entry-frozen 1.0x range projection.
The house 2xATR stop / 3xATR trail sit behind the signal
exit, with a 120-bar max hold. No longs ever fire.

Source: Wyckoff distribution schematic — Wyckoff method --
https://www.cmcmarkets.com/en-gb/trading-strategy/what-is-wyckoff-method

## Limitations

- 90 trades, 64 of them stop exits: the backtest mostly
  measures the stop, not the schematic's exits.
- The 120-bar max hold never binds (0 max_hold exits) --
  trades resolve via stop or signal exit first.
- BTC's SOW/LPSY chain (1 each) is too thin to say anything
  about the full chain on BTC; the result is dominated by
  raw UTAD-reclaim entries.
- Single ~8.4-month crypto window; funding unmodeled;
  next-bar-open execution vs idealized entry.
- Never tune the shipped reclaim window or range window on
  this window.
