# MACD Divergence (MACD-only) — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), pinned window: 2026-03-14 22:00 UTC → 2026-11-22 14:00 UTC
(BTC 6,064 bars, ETH 6,064 bars, HYPE 6,062 bars — exactly the
expected counts).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR(14) stop, 3x
leverage cap, $10k start, long/short. WARMUP=60 bars.

## Results (shipped config: regular MACD-histogram divergence on
confirmed ±2-bar pivots, histogram-rising/falling entry filter,
zero-cross or opposite-divergence exit, 2xATR(14) stop,
120-bar max hold; MACD-only, no RSI divergence)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 131 | 33.6% | -$2,060 | -20.6% | -1.83 | -26.8% | -$15.73 | 0.69 |
| ETH | 133 | 39.8% | +$921 | +9.2% | +0.78 | -19.1% | +$6.93 | 1.13 |
| HYPE | 138 | 38.4% | +$1,189 | +11.9% | +0.89 | -16.2% | +$8.62 | 1.17 |
| **Combined** | **402** | **37.3%** | **+$50** | — | — | — | **+$0.12** | — |

Fees: BTC $1,270, ETH $1,169, HYPE $743 (total $3,182).

Exit reasons: BTC 76 signal / 55 stop; ETH 86 signal / 47 stop;
HYPE 89 signal / 49 stop. No max-hold exits — the zero-cross
or opposite-divergence exit always fired first. Sides roughly
balanced (BTC 72 long / 59 short; ETH 64 / 69; HYPE 67 / 71).

## Verdict: breakeven — a scratch, not an edge

Combined +$50 across 402 trades with a 37.3% win rate and a
+$0.12 expectancy is breakeven to the dollar. That is the
honest verdict: the system neither wins nor loses on this
window, and +$50 on 402 trades is noise, not an edge. Do not
quote it as a winner.

- The per-coin split is the story: BTC -$2,060 (Sharpe -1.83,
  PF 0.69) while ETH +$921 and HYPE +$1,189. The same rules
  lose badly on the coin that trended down hardest and win
  modestly on the other two — the result is regime-dependent,
  and the BTC leg shows what the system does in a sustained
  downtrend: it keeps buying lower lows on divergence that
  never turns, and the 2xATR stop eats 42% of its exits.
- Fees ($3,182) are 64x the net result. At ~1 trade per coin
  per 1.5 days the cost drag is material but not the deciding
  factor — the gross edge before fees is only ~+$3,232 over
  402 trades, i.e. the system is flat before costs too.
- The entry lag flagged in the README shows up in the exit
  mix: most exits are signal exits (zero-cross), meaning
  positions are typically closed by momentum rolling over
  again shortly after entry — the divergence catches a bounce
  and the bounce fades.

Stated plainly: MACD divergence on 1h crypto as built is a
coin flip. It is not a loser to the degree the Turtle is, but
there is nothing here to trade. The one direction worth a
follow-up (not in this batch) would be testing whether the
RSI-divergence variant the slug promises — which was NOT
implemented here — behaves any differently; that is a new
strategy, not a tune of this one.

## Mechanism

LONG on a lower confirmed pivot low with a higher MACD
histogram at the pivot (vs the previous pivot low) and a
rising histogram on the confirmation bar; SHORT on the mirror.
Exit on a histogram zero-cross or the opposite divergence.
2xATR(14) stop, 120-bar max hold. MACD-only — RSI divergence
not implemented. All params fixed a priori; no optimization.

Source: Gerald Appel (MACD) + classic divergence literature
(Bulkowski, *Encyclopedia of Chart Patterns*)
(https://thepatternsite.com/Divergence.html).

## Limitations

- Single 8-month crypto window; funding unmodeled;
  next-bar-open execution vs idealized entry.
- 402 trades is a large sample, but the per-coin divergence
  (BTC -20.6% vs HYPE +11.9%) shows the result is
  regime-dependent, not a stable edge.
- Never tune the shipped parameters on this window — least of
  all the ±2 pivot window or the (12, 26, 9) MACD lengths,
  which directly control how many trades fire.
