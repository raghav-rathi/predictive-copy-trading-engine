# Wyckoff Accumulation — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, read from the
local cache only (`data/candles/{BTC,ETH,HYPE}_1h.csv`), pinned
batch-48 window ms `[1773525600000, 1795788000000)`
(2026-03-14 22:00 UTC → 2026-11-27 14:00 UTC exclusive, last
bar 13:00 UTC): 6,184 bars BTC/ETH, 6,182 HYPE. Funding not
modeled (fully offline run).
**Costs:** 0.045% taker fee + 0.01% slippage per side.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start per coin. WARMUP=200 bars. LONG ONLY.

## Results (shipped config: 120-bar range, >=5% decline gate,
spring = dip below the 120-bar low reclaimed within 3 bars;
SOS = wide up bar closing above the range midpoint within 48
bars of a spring; LPS = first higher-low pullback within 24
bars of an SOS; entry on the spring-reclaim bar or an LPS
bar; exit below spring_low or above the 1.0x range
projection; 2xATR stop, 3xATR trail, 240-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor | Fees |
|---|---|---|---|---|---|---|---|---|---|
| BTC | 24 | 20.8% | -$1,019.45 | -10.2% | -2.09 | -13.2% | -$42.48 | 0.28 | $146.02 |
| ETH | 23 | 30.4% | -$382.83 | -3.8% | -0.63 | -9.4% | -$16.64 | 0.74 | $115.32 |
| HYPE | 71 | 25.4% | -$595.92 | -6.0% | -0.60 | -11.1% | -$8.39 | 0.83 | $307.56 |
| **Combined** | **118** | **25.4%** | **-$1,998.21** | **-6.7%** | **-1.44** | **-9.5%** | **-$16.93** | **0.69** | **$568.90** |

Exit-reason breakdown: BTC stop 21 / signal 3; ETH stop 22 /
signal 1; HYPE stop 57 / signal 14. Net % is the final-equity
return ($30k combined -> $28,001.79); Net $ is the sum of
closed-trade PnL.

## Verdict: the schematic fires, then the stop eats it

Combined -$1,998 on 118 trades (win rate 25.4%, PF 0.69) is
a loser, but a small and informative one: the structure
detects real events (BTC 29 springs / 3 SOS / 3 LPS, ETH 24 /
5 / 5, HYPE 82 / 10 / 10 -- the chain is rare, as a
schematic should be) and then 100 of 118 trades exit on the
2xATR hard stop, only 18 on the signal exit. The spring low
is usually only just below the entry, so the "invalidation"
and the hard stop sit almost on top of each other and the
trade has no room to breathe: the spring reclaims, price
chops, and the stop (or a close back below spring_low) takes
it out before any markup develops. HYPE trades three times
as often as BTC/ETH -- its noisier 1h tape throws far more
springs -- and still loses. The range projection exit
almost never pays: only 18 signal exits across all coins,
and the winners inside them do not cover 100 stops. Honest
read: on 1h crypto the spring is a real pattern with a real
failure mode (the reclaim does not stick), and the 2xATR
stop is too tight for a 240-bar-hold schematic. Widening
the stop would be tuning on this window, so it stays as
specified.

## Mechanism

State machine in indicators.py: the trailing 120-bar range
and a 5%-over-120-bars decline gate; a dip below the prior
range low that reclaims within 3 bars confirms a spring
(spring_low = lowest low of the dip); within 48 bars a wide
up bar closing above the range midpoint with volume
confirmation is the SOS; within 24 bars the first bar
holding above spring_low with a close above range_low is
the LPS. signals.py enters long on a spring-reclaim bar or
an LPS bar, and exits on a close below the entry-frozen
spring_low or above the entry-frozen 1.0x range projection.
The house 2xATR stop / 3xATR trail sit behind the signal
exit, with a 240-bar max hold. No shorts ever fire.

Source: Wyckoff accumulation --
https://www.chartguys.com/chart-patterns/wyckoff-accumulation

## Limitations

- 118 trades, 100 of them stop exits: the backtest mostly
  measures the stop, not the schematic's exits.
- The 240-bar max hold never binds (0 max_hold exits) --
  trades resolve via stop or signal exit first.
- Single ~8.4-month crypto window; funding unmodeled;
  next-bar-open execution vs idealized entry.
- Never tune the shipped reclaim window or SOS window on
  this window.
