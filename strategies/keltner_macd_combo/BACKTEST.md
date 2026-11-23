# Keltner Channel + MACD Combo — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), pinned window: 2026-03-14 22:00 UTC → 2026-11-22 14:00 UTC
(BTC/ETH 6,064 bars, HYPE 6,062 bars).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=40 bars.

## Results (shipped config: Keltner(20, 1.5xATR(10)) break +
MACD(12,26,9) histogram agreement; exit on close back inside
the channel or histogram flip; 2xATR harness backstop;
120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 353 | 22.7% | -$3,759 | -37.6% | -3.40 | -41.9% | -$10.65 | 0.60 |
| ETH | 325 | 22.2% | -$3,008 | -30.1% | -2.24 | -32.1% | -$9.26 | 0.67 |
| HYPE | 406 | 23.9% | -$2,028 | -20.1% | -1.61 | -25.8% | -$5.00 | 0.79 |
| **Combined** | **1,084** | **23.0%** | **-$8,795** | — | — | — | **-$8.11** | — |

Fees: BTC $3,117, ETH $2,272, HYPE $1,878 (total $7,267).

## Verdict: loser — decisively, on all three coins

This is not a marginal result. 1,084 trades, a 23.0% win rate,
profit factor 0.60–0.79, Sharpe −1.61 to −3.40, and a combined
−$8,795 (−88% of the $10k start across the three independent
$10k runs). Every coin loses by a wide margin, so there is no
single-coin story to hide behind.

- The mechanism fails as designed, not by accident. ~90% of
  trades exit on the signal (316/353 BTC, 287/325 ETH, 385/406
  HYPE), not the stop: the close is back inside the channel
  almost immediately after the breakout bar. A Keltner break on
  1h crypto is usually a one-bar excursion, and the exit rule
  dutifully takes the trade off one bar later — after paying
  entry fees and slippage both ways.
- Fees are most of the loss ($7,267 of the $8,795) but not all
  of it: gross PnL before fees is still ≈ −$1,527. Even with
  zero fees this system loses. The dual-agreement filter does
  not save it — the MACD histogram agreeing on the breakout bar
  is agreement with a move that is already spent (see README).
- The 120-bar max hold never binds (0 max-hold exits): trades
  never live long enough to need it. The 2xATR stop fires only
  ~10% of the time; the signal exit is the binding constraint.
- Win rate ~23% with profit factor 0.60 means losers outweigh
  winners in both count and size. Nothing in the table suggests
  a parameter tweak rescues this — the failure is the exit
  rule meeting 1h noise, and loosening the exit to let trades
  run would be tuning on this window, so we do not do it here.

Stated plainly: do not trade this. The channel-breakout +
MACD-agreement idea, exactly as specified from Raschke/Appel,
loses money on 1h crypto in this window.

## Mechanism

LONG on a close breaking above the upper Keltner band
(transition only) while MACD histogram > 0; exit on a close
back inside the channel or the histogram turning negative;
short mirror. All params fixed a priori; no optimization.

Source: Linda Raschke & Laurence Connors, *Street Smarts*
(1995), Keltner Channel chapter; MACD per Gerald Appel —
https://www.tradingview.com/scripts/keltner/.

## Limitations

- Single 8-month crypto window (a strong downtrend regime for
  much of it); funding unmodeled; next-bar-open execution vs
  idealized entry.
- 1,084 trades is a large sample, so the negative verdict is
  statistically meaningful for this window — but it is still
  one window and one regime; the claim is "loses here", not
  "loses everywhere".
- Never tune the shipped parameters on this window — least of
  all the exit rule, which directly controls the trade count.
