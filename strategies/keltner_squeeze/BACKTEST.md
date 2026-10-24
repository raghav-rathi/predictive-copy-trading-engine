# TTM-Style Keltner Squeeze Breakout — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), FULL cached range: BTC/ETH 2026-03-14 22:00 UTC →
2026-10-22 23:00 UTC (5,335 bars each), HYPE 2026-03-15 00:00 UTC
→ 2026-10-22 23:00 UTC (5,333 bars). 408 trades across the three
coins.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2.0xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=60 bars.

## Results (shipped config: squeeze = BB(20, 2.0) width < KC(EMA20,
1.5×ATR10) width; entry = squeeze on within last 3 bars + close
outside the Bollinger Band; exit = opposite band cross; 2.0xATR
stop, 2.5xATR chandelier trail, 96-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 138 | 37.7% | -$788 | -7.9% | -0.59 | -18.1% | -$5.71 | 0.87 |
| ETH | 137 | 39.4% | +$2,042 | +20.4% | +1.52 | -11.0% | +$14.90 | 1.33 |
| HYPE | 133 | 30.8% | -$354 | -2.0% | -0.05 | -17.6% | -$2.66 | 0.95 |
| **Combined** | **408** | — | **+$900** | — | — | — | — | — |

Fees: BTC $1,612, ETH $1,314, HYPE $651 (total $3,577).
Long/short split: BTC longs +$297 / shorts -$1,084; ETH longs
+$1,895 / shorts +$147; HYPE longs +$2,267 / shorts -$2,622.
Exit reasons: 396 stop, 12 signal, 0 max-hold.

## Verdict: mixed — one good leg, two flat legs, no aggregate edge

Combined +$900 across 408 trades is break-even after the noise
is accounted for: the ETH leg (+$2,042, Sharpe +1.52, PF 1.33)
is genuinely good, but BTC (-$788, PF 0.87) and HYPE (-$354,
PF 0.95) give it straight back, and a single-leg winner among
three is exactly what multiple comparisons produces. The
long/short split is the more interesting signal: longs are
+$4,459 in aggregate while shorts are -$3,559 — the squeeze
breakout works with the window's upside drift and fights it on
the short side (HYPE shorts -$2,622 against HYPE longs
+$2,267 is the extreme case).

The exit reasons are a warning about the exit design, not the
entry: 396 of 408 trades exit on the stop/trail and only 12 on
the opposite-band signal. The opposite-band cross is so far
away that it almost never fires — the trail is doing all the
exiting, which means the strategy as traded is really "squeeze
breakout + 2.5xATR chandelier exit," and the documented signal
exit is decorative. That is not a flaw to patch on this window,
but any revisit should either tighten the signal exit (e.g.,
mid-band cross) or admit the trail is the exit and size
accordingly.

Honest read: not tradeable as a standalone system on this
evidence — ETH's leg is worth watching on walk-forward data,
and a long-only variant is the first thing to test there, but
neither claim survives on this window alone.

## Mechanism

Squeeze ON = BB(20, 2.0) width < KC(EMA20 ± 1.5×ATR10) width.
Long: squeeze on within last 3 bars + close crosses above the
BB upper band. Short: mirror. Exit: opposite band cross.
2.0xATR stop, 2.5xATR chandelier trail, 96-bar max hold. All
params fixed a priori; no optimization.

Sources: https://school.stockcharts.com/doku.php?id=technical_indicators:keltner_channels

## Limitations

- Single ~7-month crypto window; 408 trades across three coins
  is a moderate sample, and the legs disagree.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped parameters on this window.
