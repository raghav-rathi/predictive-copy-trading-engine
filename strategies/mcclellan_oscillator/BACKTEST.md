# McClellan Oscillator — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 22:00 UTC → 2026-11-16 14:00 UTC
(ms `[1773525600000, 1794837600000)`): 5,920 bars BTC/ETH, 5,918 HYPE.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 1.5xATR stop, 3x leverage cap,
$10k start. WARMUP=60 bars.

## Results (shipped config: RANA(24), EMA19/EMA39 oscillator, cross
above/below 0 after a ±50 excursion with the summation index confirming,
exit on a cross back through 0 or the summation turning, 1.5xATR stop,
2.5xATR target, 48-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor | Fees $ |
|---|---|---|---|---|---|---|---|---|---|
| BTC | 56 | 32.1% | -$1,038 | -10.4% | -1.25 | -14.2% | -$18.53 | 0.71 | $739 |
| ETH | 63 | 30.2% | -$1,492 | -14.9% | -1.86 | -17.6% | -$23.68 | 0.64 | $596 |
| HYPE | 71 | 32.4% | -$1,451 | -14.5% | -1.80 | -19.0% | -$20.44 | 0.70 | $455 |
| **Combined** | **190** | **31.6%** | **-$3,980** | — | — | — | **-$20.95** | — | **$1,791** |

Signal gates fire on every coin (long entries 27/33/33, short entries
29/30/38 for BTC/ETH/HYPE). Win rates sit at 30–32% on all three
coins with profit factors of 0.64–0.71 — the breadth-thrust entries
are systematically on the wrong side of the next 48 bars.

## Verdict: loser on all three coins

Combined -$3,980 across 190 trades (expectancy -$20.95/trade) with
no coin better than -10.4%. The single-asset candle-count proxy does
not carry the information real exchange breadth does: up/down candle
counts on one asset are mostly a relabeling of that asset's own
returns, so the "breadth thrust" is just a lagged momentum signal
that buys tops and sells bottoms. Nothing here survives.

## Calibration note

Shipped the specified EMA19/EMA39. A 10/21 – 19/39 – 30/50 sweep is
in CALIBRATION.md: no setting is green on all three coins, and the
30/50 setting's near-zero combined (-$79) rests on 24 trades total.
The 19/39 setting was fixed a priori — adopted before the sweep,
not because of it.

## Mechanism

RANA = 1000·(up−down)/(up+down) over 24 bars (up = close > open,
down = close < open, dojis neutral); oscillator = EMA19(RANA) −
EMA39(RANA); summation index = cumulative oscillator. Long on a
cross above 0 after a sub −50 excursion with a rising summation
index; short mirrored. Exit on a cross back through 0 or the
summation index turning against the position. 1.5xATR stop, 2.5xATR
target, 48-bar max hold.

Sources: McClellan Oscillator (AAII) —
https://www.aaii.com/journal/article/347760-looking-beyond-price-trends-with-the-mcclellan-oscillator
and https://patternswizard.com/mcclellan-oscillator/

## Limitations

- Single-asset candle-count proxy for exchange breadth, not true
  advance/decline data — the core caveat; the backtest says the
  proxy does not work on 1h crypto.
- Single 8-month crypto window; 190 trades, win rate ~32% on every
  coin — the loss is consistent, not a one-coin accident.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped EMA lengths on this window (see CALIBRATION.md).
