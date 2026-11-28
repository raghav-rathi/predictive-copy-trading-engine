# Garman-Klass Volatility Expansion — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, read from the
local cache only (`data/candles/{BTC,ETH,HYPE}_1h.csv`), pinned
batch-49 window ms `[1773525600000, 1795874400000)`
(2026-03-14 22:00 UTC → 2026-11-28 14:00 UTC exclusive; cache
ends 2026-11-27 14:00 UTC, last bar 13:00 UTC): 6,185 bars
BTC/ETH, 6,183 HYPE. Funding not modeled (fully offline run).
**Costs:** 0.045% taker fee + 0.01% slippage per side.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start per coin. WARMUP=80 bars.

## Results (shipped config: GK vol window 20, vol SMA 60,
EMA(20); entry on gk_vol crossing above its SMA with the
close on the EMA20 side; exit on vol crossing back below
its SMA or the close crossing the wrong side of EMA20;
2xATR stop, 3xATR trail, 72-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor | Fees |
|---|---|---|---|---|---|---|---|---|---|
| BTC | 140 | 31.4% | -$821.05 | -8.2% | -0.70 | -21.2% | -$5.86 | 0.84 | $1,347.07 |
| ETH | 144 | 31.9% | -$1,491.82 | -14.9% | -1.40 | -21.8% | -$10.36 | 0.74 | $1,041.10 |
| HYPE | 140 | 37.9% | -$150.38 | -1.5% | -0.07 | -8.7% | -$1.07 | 0.97 | $653.10 |
| **Combined** | **424** | **33.7%** | **-$2,463.25** | **-8.2%** | **-1.06** | **-12.7%** | **-$5.81** | **0.85** | **$3,041.26** |

Exit-reason breakdown: BTC signal 80 / stop 60; ETH signal 82 /
stop 62; HYPE signal 91 / stop 49. No max-hold exits, no
targets (target is off). Net % is the final-equity return
($30k combined -> $27,536.75); Net $ is the sum of
closed-trade PnL.

## Verdict: a thin edge that fees eat whole

Combined -$2,463.25 on 424 trades (win rate 33.7%, PF 0.85)
is a loser, but it is a *fee* loser, not a signal loser:
gross PnL before the $3,041.26 of fees is +$578.01. The
vol-expansion trigger does find slightly positive
pre-cost drift -- the best result in the batch-49 pair by
gross PnL -- but 0.055% per side round-trip on ~140
trades per coin swallows it. The signal exit does most of
the work (253 of 424 trades): volatility expands, the trade
is entered, volatility contracts again, and the trade is
closed -- usually for a small win or small loss. The 2xATR
stop takes the other 171, and those are the expensive ones:
the average losing trade is bigger than the average winner
(PF 0.85 at a 33.7% win rate). Side split is the honest
detail: shorts lose on every coin (BTC -$794, ETH -$963,
HYPE -$1,088) while longs are near breakeven (BTC -$27,
ETH -$529, HYPE +$938). In a mostly down-drifting window,
the short side of a vol-expansion trigger still loses --
expansions in a downtrend are mostly counter-trend squeezes
that the EMA20 gate lets through and the stop then pays
for. Honest read: the estimator works as advertised
(realized vol does expand before moves), but "vol expanded
+ trend filter" on 1h bars has no post-cost edge, and the
short side is the drag.

## Comparison with parkinson_volatility (same trade structure)

The Parkinson twin loses less: combined -$605.77 on the
same 424 trades (PF 0.96, Sharpe -0.16 vs -1.06 here).
The difference is almost entirely HYPE longs: Parkinson
HYPE longs make +$2,126 vs +$938 here, and Parkinson HYPE
is the only profitable coin in either strategy (+$1,733.63,
PF 1.35, Sharpe +1.45). The GK open/close correction term
is supposed to be the *more* efficient estimator; on this
window it is the worse trader -- the correction term
re-times a handful of entries and exits, and the re-timing
costs money on HYPE. Both strategies share the same
failure mode (shorts lose everywhere, fees eat the gross
edge), so the estimator is not what decides outcomes here.
Neither strategy is shippable: the best combined result in
the pair is still a loser after costs.

## Mechanism

indicators.py: per-bar GK variance 0.5*ln(H/L)^2 -
(2 ln2 - 1)*ln(C/O)^2, clipped at >= 0 per bar, averaged
over 20 bars and square-rooted to gk_vol; SMA(gk_vol, 60);
EMA(close, 20); ATR(14) for risk. signals.py enters on
crossed_above(gk_vol, gk_vol_sma) gated by close vs EMA20
(long above, short below), enters neither if both would
fire on one bar (impossible in practice -- the close cannot
be both above and below EMA20), and exits on
crossed_below(gk_vol, gk_vol_sma) or the close crossing
the wrong side of EMA20. The house 2xATR stop / 3xATR
trail sit behind the signal exit, with a 72-bar max hold
that never binds.

Sources: Garman & Klass (1980) --
https://kaisquant.com/posts/range-volatility-estimators/

## Limitations

- 424 trades is a decent sample, but the combined result
  (-$2,463) is small relative to per-trade noise
  (expectancy -$5.81 +/- a large standard error): the
  "loser" verdict is firm on costs, soft on the signal.
- The 72-bar max hold never binds (0 trades) -- the signal
  exit and the stop do all the exiting.
- Single ~8.4-month crypto window, all three coins in the
  same down-drifting regime for much of it; funding
  unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped vol window or vol-SMA length on
  this window.
