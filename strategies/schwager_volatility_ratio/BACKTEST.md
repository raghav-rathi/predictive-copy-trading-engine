# Schwager Volatility Ratio — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 22:00 UTC → 2026-11-16 14:00 UTC
(ms `[1773525600000, 1794837600000)`): 5,920 bars BTC/ETH, 5,918 HYPE.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=30 bars.

## Results (shipped config: VR > 2.0 fade, 2xATR stop, 3xATR target,
10-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 191 | 42.9% | -$3,595 | -36.0% | -3.77 | -36.0% | -$18.82 | 0.59 |
| ETH | 186 | 43.0% | -$3,186 | -31.9% | -3.19 | -31.9% | -$17.13 | 0.62 |
| HYPE | 138 | 42.8% | -$2,030 | -20.3% | -2.38 | -26.4% | -$14.71 | 0.66 |
| **Combined** | **515** | **42.9%** | **-$8,810** | — | — | — | **-$17.11** | — |

Wide bars fire often (long entries 103/97/63, short entries 93/95/77
for BTC/ETH/HYPE) and 515 of them become trades. Fees total $3,660
against a -$8,810 net — the loss is not fee drag, it is the signal:
fading a wide bar that closes at its extreme loses when the bar is
continuation, and in this window it usually was. Every coin is down
more than 20% with Sharpe below -2.3.

## Verdict: worst of the batch — the fade is structurally wrong here

Combined -$8,810 on 515 trades with expectancy -$17.11/trade and
profit factor 0.59–0.66 on every coin is a decisive rejection, not a
tuning problem: the win rate (~43%) is fine for a 1.5R payoff, but
the average win is far smaller than the average loss, so the target
almost never prints before the stop or the 10-bar exit. A mean-
reversion fade needs a ranging regime; the Mar–Nov 2026 window,
including the early-Nov selloff, did not provide one.

## Calibration note

Shipped the specified VR > 2.0. A 1.5 – 2.0 – 2.5 threshold sweep is
in CALIBRATION.md: every setting is deeply red combined (-$11,027 /
-$8,810 / -$5,204), and no setting is green on any coin. Raising the
threshold only loses less by trading less. The 2.0 threshold was
fixed a priori — adopted before the sweep, not because of it.

## Mechanism

VR = true range / EMA(TR, 14) of prior bars (current bar excluded).
A VR > 2.0 bar closing in its lower quarter with a negative 5-bar
return is faded long; the mirror is faded short. Exit on the
opposite wide bar, a 3xATR target (1.5R vs the 2xATR stop), or the
10-bar time exit. The 2xATR stop approximates "just beyond the wide
bar's extreme". Entries execute at the next bar's open (harness
deviation from the spec's "next 1h close" — see README).

Source: Schwager Volatility Ratio —
https://www.incrediblecharts.com/indicators/volatility_ratio_schwager.php

## Limitations

- Single 8-month crypto window, and a strongly trending one — the
  result is regime-conditional, but the regime is the one that
  matters for a fade.
- The 2xATR stop is an approximation of the textbook wide-bar-extreme
  stop, not the literal level (see risk.py).
- Funding unmodeled; next-bar-open execution vs the spec's next-close
  entry.
- Never tune the shipped VR threshold on this window (see CALIBRATION.md).
