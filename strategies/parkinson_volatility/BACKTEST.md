# Parkinson Volatility Expansion — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, read from the
local cache only (`data/candles/{BTC,ETH,HYPE}_1h.csv`), pinned
batch-49 window ms `[1773525600000, 1795874400000)`
(2026-03-14 22:00 UTC → 2026-11-28 14:00 UTC exclusive; cache
ends 2026-11-27 14:00 UTC, last bar 13:00 UTC): 6,185 bars
BTC/ETH, 6,183 HYPE. Funding not modeled (fully offline run).
**Costs:** 0.045% taker fee + 0.01% slippage per side.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start per coin. WARMUP=80 bars.

## Results (shipped config: Parkinson vol window 20, vol SMA
60, EMA(20); entry on pk_vol crossing above its SMA with
the close on the EMA20 side; exit on vol crossing back below
its SMA or the close crossing the wrong side of EMA20;
2xATR stop, 3xATR trail, 72-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor | Fees |
|---|---|---|---|---|---|---|---|---|---|
| BTC | 129 | 32.6% | -$1,217.14 | -12.2% | -1.10 | -24.1% | -$9.44 | 0.76 | $1,208.95 |
| ETH | 149 | 33.6% | -$1,122.25 | -11.2% | -0.98 | -16.6% | -$7.53 | 0.79 | $1,042.70 |
| HYPE | 146 | 38.4% | +$1,733.63 | +17.8% | +1.45 | -8.5% | +$11.87 | 1.35 | $760.74 |
| **Combined** | **424** | **34.9%** | **-$605.77** | **-2.0%** | **-0.16** | **-9.0%** | **-$1.43** | **0.96** | **$3,012.39** |

Exit-reason breakdown: BTC signal 69 / stop 60; ETH signal 90 /
stop 59; HYPE signal 98 / stop 48. No max-hold exits, no
targets (target is off). Net % is the final-equity return
($30k combined -> $29,442.73); Net $ is the sum of
closed-trade PnL.

## Verdict: the better twin, still a loser after costs

Combined -$605.77 on 424 trades (win rate 34.9%, PF 0.96)
is the closest to breakeven in the batch-49 pair, and like
its twin it is a *fee* loser: gross PnL before the
$3,012.39 of fees is +$2,406.62. The vol-expansion trigger
does find positive pre-cost drift -- better gross than
Garman-Klass (+$578) -- but 0.055% per side round-trip on
~140 trades per coin still swallows it. The signal exit
does most of the work (257 of 424 trades): volatility
expands, the trade is entered, volatility contracts again,
and the trade is closed -- usually for a small win or small
loss. The 2xATR stop takes the other 167. The one bright
spot is HYPE: +$1,733.63 (PF 1.35, Sharpe +1.45, the only
profitable coin in either strategy), driven by HYPE longs
(+$2,126) against HYPE shorts (-$393). Side split across
the board: longs are +$1,934 combined (BTC -$227, ETH +$35,
HYPE +$2,126) while shorts lose on every coin (BTC -$990,
ETH -$1,158, HYPE -$393). In a mostly down-drifting window,
the short side of a vol-expansion trigger still loses --
expansions in a downtrend are mostly counter-trend squeezes
that the EMA20 gate lets through and the stop then pays
for. Honest read: the Parkinson estimator plus this trade
structure has a real pre-cost signal on HYPE longs and
nothing elsewhere; after costs the whole package is a
small loser, and the HYPE result is one coin in one window
-- not a basis for shipping.

## Comparison with garman_klass_volatility (same trade structure)

The Garman-Klass twin loses more: combined -$2,463.25 on
the same 424 trades (PF 0.85, Sharpe -1.06 vs -0.16 here).
The difference is almost entirely HYPE longs: Parkinson
HYPE longs make +$2,126 vs +$938 for GK, and Parkinson
HYPE is the only profitable coin in either strategy
(+$1,733.63, PF 1.35, Sharpe +1.45). The GK open/close
correction term is supposed to be the *more* efficient
estimator; on this window it is the worse trader -- the
correction term re-times a handful of entries and exits,
and the re-timing costs money on HYPE. Both strategies
share the same failure mode (shorts lose everywhere, fees
eat the gross edge), so the estimator is not what decides
outcomes here. Neither strategy is shippable: the best
combined result in the pair is still a loser after costs.

## Mechanism

indicators.py: per-bar Parkinson variance ln(H/L)^2 /
(4 ln2), averaged over 20 bars and square-rooted to
pk_vol; SMA(pk_vol, 60); EMA(close, 20); ATR(14) for
risk. signals.py enters on crossed_above(pk_vol,
pk_vol_sma) gated by close vs EMA20 (long above, short
below), enters neither if both would fire on one bar
(impossible in practice -- the close cannot be both above
and below EMA20), and exits on crossed_below(pk_vol,
pk_vol_sma) or the close crossing the wrong side of EMA20.
The house 2xATR stop / 3xATR trail sit behind the signal
exit, with a 72-bar max hold that never binds.

Sources: Parkinson (1980) --
https://kaisquant.com/posts/range-volatility-estimators/

## Limitations

- 424 trades is a decent sample, but the combined result
  (-$605.77) is small relative to per-trade noise
  (expectancy -$1.43 +/- a large standard error): the
  "loser" verdict is firm on costs, soft on the signal --
  and the HYPE win (+$1,734) is one coin in one window,
  not evidence of a HYPE-specific edge.
- The 72-bar max hold never binds (0 trades) -- the signal
  exit and the stop do all the exiting.
- Single ~8.4-month crypto window, all three coins in the
  same down-drifting regime for much of it; funding
  unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped vol window or vol-SMA length on
  this window.
