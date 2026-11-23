# Stochastic + Bollinger %b — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), pinned window: 2026-03-14 22:00 UTC → 2026-11-22 14:00 UTC
(BTC 6,064 bars, ETH 6,064 bars, HYPE 6,062 bars).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=40 bars.

## Results (shipped config: Bollinger(20,2); Stochastic(14,3,3);
long on %K cross above %D with %b < 0.2 and %K < 30; exit on
%b > 0.8 or %K cross below %D; short mirror; 2xATR stop; no
trail/target; 120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 261 | 29.5% | -$2,506 | -25.1% | -2.64 | -27.9% | -$9.60 | 0.69 |
| ETH | 260 | 33.1% | -$1,644 | -16.4% | -1.53 | -18.1% | -$6.32 | 0.80 |
| HYPE | 294 | 32.3% | -$3,666 | -36.7% | -4.02 | -38.7% | -$12.47 | 0.58 |
| **Combined** | **815** | **31.7%** | **-$7,816** | — | — | — | **-$9.59** | — |

Fees: BTC $2,699, ETH $2,047, HYPE $1,160 (total $5,906).

Exit reasons: signal 224 / stop 37 (BTC), 222 / 38 (ETH),
248 / 46 (HYPE) — the signal exit (opposite band or %K rollover)
does most of the work; the 2xATR stop fires on ~14–16% of trades.
Longs/shorts roughly balanced (BTC 124/137, ETH 121/139,
HYPE 136/158).

## Verdict: loser — the double-oversold gate buys downtrends

All three coins lose, with negative Sharpe on all three and a
combined -$7,816 over 815 trades. This is not a small-sample
fluke: 815 trades is the largest sample of any batch-44
strategy so far, and the loss is consistent across coins
(BTC -25%, ETH -16%, HYPE -37%). The mechanism fails the way
the README warned it could: in the Mar–Nov 2026 window all
three coins spent long stretches trending down, and buying the
lower band on a %K cross into a downtrend catches falling
knives — %K crosses up on every dead-cat bounce, %b < 0.2
stays true for the whole leg down, and the exit (%b > 0.8 or
%K rolling over) usually triggers on the bounce failing rather
than on a completed reversion.

- Win rate ~30–33% with profit factor 0.58–0.80: losers are
  bigger than winners, not just more frequent.
- Fees are a large share of the damage but not the cause: BTC
  and ETH were roughly break-even before fees (gross +$193 and
  +$403), HYPE lost -$2,506 before fees. Even at zero fees
  the combined result would be about -$1,910 — still a loser,
  just a smaller one.
- Max drawdowns of -18% to -39% on a 1%-risk system show the
  losses cluster: the system loses repeatedly through the same
  downtrend legs instead of spreading losses evenly.

Stated plainly: do not trade this as specified on 1h crypto.
The %b + Stochastic combination is a textbook mean-reversion
setup that needs a ranging market; this window did not provide
one, and the system has no trend filter to sit it out.

## Mechanism

LONG on %K crossing above %D while %b < 0.2 and %K < 30;
exit long on %b > 0.8 or %K crossing below %D; short mirror.
All params fixed a priori; no optimization.

Source: John Bollinger, *Bollinger on Bollinger Bands* (2001),
%b chapter (https://www.bollingerbands.com/).

## Limitations

- Single 8-month crypto window, heavily trend-down in the
  second half; funding unmodeled; next-bar-open execution vs
  idealized entry.
- No trend filter by design — that is the tested hypothesis,
  and it failed here; adding one would be a new strategy, not
  a calibration of this one.
- Never tune the shipped parameters on this window — least of
  all the 0.2/0.8 %b gates, which directly control how many
  trades fire.
