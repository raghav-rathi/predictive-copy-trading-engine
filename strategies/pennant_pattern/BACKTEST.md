# Pennant Pattern — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), filtered to t >= 1773525600000: BTC/ETH 5,445 bars,
2026-03-14 22:00 UTC → 2026-10-27 13:00 UTC; HYPE 5,443 bars,
2026-03-15 00:00 UTC → 2026-10-27 13:00 UTC.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run, funding off).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=40 bars.

## Results (shipped config: completed 5-bar pole >=3x ATR, 5–15
bar converging range via 3-bar blocks, breakout close + volume >
1.2x 20-bar average, opposite-breakout or 168-bar max hold exit,
2xATR stop, 2.5xATR trail)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 10 | 30.0% | +$48.92 | +0.49% | +0.18 | -3.56% | +$4.89 | 1.12 |
| ETH | 8 | 37.5% | +$118.41 | +1.18% | +0.42 | -3.34% | +$14.80 | 1.34 |
| HYPE | 6 | 16.7% | -$326.39 | -3.26% | -1.70 | -3.42% | -$54.40 | 0.04 |
| **Combined** | **24** | — | **-$159.06** | — | — | — | **-$6.63** | — |

Fees: BTC $85.64, ETH $65.33, HYPE $29.51 (total $180.48).
Signal entries: BTC 5 long / 5 short, ETH 4 / 4, HYPE 3 / 3.

## Verdict: flat-to-loser, thin sample

-$159.06 on 24 trades is effectively flat — but flat with a
negative sign and a HYPE leg that lost on 5 of 6 trades. BTC and
ETH's small greens (profit factors 1.12 / 1.34) are within noise
at 8–10 trades each. Nothing here clears any live gate: the
honest read is "no edge detected, sample too thin to say more".

## Mechanism

Completed 5-bar pole >=3x ATR(14) with a stalled last bar, 5–15
bar converging range (3-bar blocks: highs falling, lows rising),
volume-confirmed breakout entry, opposite-breakout or 168-bar
max hold exit, 2xATR stop, 2.5xATR trail. All params fixed a
priori; no optimization.

## Limitations

- 24 trades total; HYPE's 6 trades say nothing on their own.
- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.
