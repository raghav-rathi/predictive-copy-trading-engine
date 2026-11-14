# Kase DevStop — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 22:00 UTC → 2026-10-18 13:00 UTC
(ms `[1773525600000, 1792328400000)`): 5,223 bars BTC/ETH, 5,221 HYPE.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 6xATR disaster-stop distance,
3x leverage cap, $10k start per coin. WARMUP=60 bars.

## Results (shipped config: DTR(30), band = mean + 1.0×sample-std,
flip long on a close above the short stop, flip short on a close below
the long stop, DevStop line IS the exit, 6xATR disaster stop only, no
trail, 300-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 390 | 32.3% | -$1,812 | -17.9% | -2.88 | -21.5% | -$4.65 | 0.72 |
| ETH | 360 | 36.4% | -$388 | -3.6% | -0.42 | -14.6% | -$1.08 | 0.93 |
| HYPE | 371 | 37.7% | +$399 | +4.0% | +0.65 | -6.2% | +$1.08 | 1.07 |
| **Combined** | **1,121** | **35.4%** | **-$1,800** | — | — | — | -$1.61 | — |

Entry gates fire on every coin (BTC 198 long / 198 short flips,
ETH 181 / 181, HYPE 187 / 187).

## Verdict: a loser — the DevStop works as designed, and still loses

Combined -$1,800 across 1,121 trades, expectancy -$1.61 a trade.
Two of three legs are red (BTC -$1,812 at Sharpe -2.88, the worst
Sharpe of either strategy in this batch; ETH -$388, PF 0.93) and the
one green leg, HYPE (+$399, PF 1.07, Sharpe +0.65), is barely above
noise — its fees ($628) are 1.6x its net.

The design itself behaved exactly as specified, which is the
informative part:

- **The DevStop drives the exits.** Exit reasons: BTC 385 signal /
  5 stop, ETH 353 / 7, HYPE 371 / 0. The 6xATR disaster backstop
  fired only 12 times in 1,121 trades — the DevStop line is doing
  the exiting, as intended. The loss is not a harness artifact.
- **The failure is frequency.** 1,121 trades in 7 months — roughly
  5 flips a day across the three coins — is far too many for a
  "volatility stop" that is supposed to sit outside normal noise.
  The band (mean DTR + 1 std) is simply too tight for 1h crypto:
  closes keep tagging the stop on ordinary chop, so the system
  churns through full 1%-risk losses at a 32–38% win rate with
  profit factors of 0.72–1.07. The sensitivity sweep in
  CALIBRATION.md confirms the direction: widening the band to 1.5
  std cuts trades to 879 and losses to -$1,079, but still does not
  turn the system green.
- **No coin is a win.** Even HYPE's +$399 is a coin flip with fees
  attached. There is no leg to lean on here, unlike the
  Supertrend batch-mate where HYPE at least paid.

Treat this as a confirmed NO-GO on the published defaults for 1h
crypto: the DevStop concept is sound, but mean(DTR,30) + 1 std is
not wide enough for this timeframe. A wider band or a longer DTR
window would be a different strategy, not a calibration tweak —
and the 1.5-std sweep shows even that does not fix it.

## Calibration note

Shipped the specified Kase defaults (DTR 30, 1.0 std) a priori. The
0.5/1.0/1.5-std sweep is in CALIBRATION.md: 1.5 std is the in-sample
least-bad (-$1,079) and 0.5 std the worst (-$2,824). No setting is
switched to on the strength of this window.

## Mechanism

Kase DevStop (1996): DTR = two-bar true range; band = mean(DTR,30) +
1.0×sample-stddev(DTR,30); long stop = ratcheted highest-high-since-
flip minus band, short stop = ratcheted lowest-low-since-flip plus
band. Flip long on a close above the short stop, flip short on a
close below the long stop; the DevStop line is the exit. Harness:
6xATR disaster stop only, no trail, 300-bar max hold.

Sources: https://docs.wickra.org/Indicators/Indicator-KaseDevStop
and https://www.luxalgo.com/library/concept/kase-studies/

## Limitations

- Single 7-month crypto window; 1,121 trades is a large sample for
  the wrong reason — the system over-trades.
- All three legs red-or-noise; the combined loss is broad-based,
  not one bad coin.
- The 1.0-std band is too tight for 1h crypto ranges; widening it
  helps but does not fix the sign (see CALIBRATION.md).
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped band multiplier on this window
  (see CALIBRATION.md).
