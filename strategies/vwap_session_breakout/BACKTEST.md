# VWAP Session Breakout — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), pinned window: 2026-03-14 22:00 UTC → 2026-11-22 14:00 UTC
(BTC 6,064 bars, ETH 6,064 bars, HYPE 6,062 bars).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=24 bars.

## Results (shipped config: session VWAP +/- 1.0 volume-weighted
SD, UTC-midnight anchor; long on close crossing above the upper
band with above-average session volume; exit on a close back
below VWAP; short mirror; 2xATR stop; no trail/target; 24-bar
max hold; NO ADX filter)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 433 | 28.4% | -$5,005 | -50.2% | -3.75 | -53.2% | -$11.56 | 0.64 |
| ETH | 416 | 30.8% | -$3,341 | -33.1% | -1.95 | -43.1% | -$8.03 | 0.76 |
| HYPE | 383 | 35.0% | +$745 | +8.4% | +0.59 | -16.8% | +$1.95 | 1.05 |
| **Combined** | **1,232** | **31.2%** | **-$7,600** | — | — | — | **-$6.17** | — |

Fees: BTC $3,578, ETH $3,004, HYPE $2,158 (total $8,740).

Exit reasons: signal 352 / stop 77 / max_hold 4 (BTC),
338 / 75 / 3 (ETH), 330 / 46 / 7 (HYPE) — the VWAP-reclaim
signal exit does most of the work; the 2xATR stop fires on
~12–18% of trades; the 24-bar max hold almost never binds
(14 trades total), because the VWAP-reclaim exit fires first.
Longs/shorts roughly balanced (BTC 222/211, ETH 213/203,
HYPE 191/192).

## Verdict: loser — the raw VWAP breakout has no edge here,
and fees decide the combined sign

BTC and ETH lose heavily (Sharpe -3.75 and -1.95, drawdowns
-53% and -43% on a 1%-risk system), HYPE wins a marginal
+$745 (profit factor 1.05, Sharpe +0.59 on 383 trades — a
coin flip with a small positive drift, not an edge). Combined
-$7,600 over 1,232 trades, the largest sample in the batch,
is a clear loser.

Two honest qualifications, neither of which rescues it:

- **Fees decide the combined sign.** Before fees the combined
  result is +$1,140 (BTC -$1,427, ETH -$337, HYPE +$2,904).
  The system's gross edge, if any, is ~+$0.93/trade — far too
  thin to survive 0.055%/side of fee + slippage on ~1.6
  trades a day. A breakout system that fires this often needs
  a much larger per-trade edge to be viable; this one does not
  have it.
- **The HYPE win does not generalize.** HYPE's +$745 comes
  with a 35% win rate and a 1.05 profit factor; one bad week
  flips it. BTC and ETH, the deeper and more liquid coins,
  both lose by thousands. Do not quote the HYPE row as
  evidence the system works.

The mechanism fails the way the README warned it could: a
1.0-SD band on 1h bars is crossed constantly (hence ~400
trades per coin), most crosses are noise rather than session
acceptance of a new price, and the VWAP-reclaim exit cuts
winners at the first pullback while the 2xATR stop takes the
full loss on the crosses that run the wrong way. Win rate
~28–35% with profit factor 0.64–0.76 says the same thing from
the other side: losers are bigger than winners.

Stated plainly: do not trade the raw session-VWAP breakout on
1h crypto. The comparison with `vwap_bollinger_bands` (which
fades the bands only in a ranging regime) is the useful
result here: the regime gate was doing real work, and removing
it leaves a system that churns.

## Mechanism

LONG on close crossing above VWAP + 1.0 SD with bar volume
above the session average; exit long on a close back below
VWAP; short mirror; no ADX or other regime filter. All params
fixed a priori; no optimization.

Source: Brian Shannon, *Technical Analysis Using Multiple
Timeframes* (2008), VWAP chapter
(https://www.alphatrends.net/).

## Limitations

- Single 8-month crypto window; funding unmodeled;
  next-bar-open execution vs idealized entry.
- UTC-midnight anchor is an adaptation, not a market open —
  early-session bands are built from few bars (see README).
- Never tune the shipped parameters on this window — least of
  all the 1.0-SD band width or the volume gate, which directly
  control how many trades fire.
