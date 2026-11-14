# Dynamic Zones RSI — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 22:00 UTC → 2026-10-18 13:00 UTC
(ms `[1773525600000, 1792328400000)`; actual data starts 2026-03-14
22:00 UTC for BTC/ETH, 2026-03-15 00:00 UTC for HYPE): 5,223 bars
BTC/ETH, 5,221 HYPE.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=100 bars.

## Results (shipped config: RSI(14), buy zone = 12th percentile / sell
zone = 88th percentile over rolling 70 bars, long on a cross back
above the buy zone, short on a cross back below the sell zone, exits
at RSI crossing 50 or opposite zone touch, 2xATR stop, 3xATR trail,
120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 342 | 35.1% | -$5,623 | -56.4% | -5.90 | -56.6% | -$16.44 | 0.52 |
| ETH | 318 | 39.0% | -$3,875 | -38.7% | -3.34 | -45.3% | -$12.19 | 0.69 |
| HYPE | 312 | 43.6% | -$3,017 | -30.2% | -2.61 | -36.6% | -$9.67 | 0.75 |
| **Combined** | **972** | **39.1%** | **-$12,515** | — | — | — | **-$12.88** | — |

Entry gates all fire on every coin (long entries 197–235, short
entries 214–244 per coin).

## Verdict: a loser on all three coins

Combined -$12,515 across 972 trades, and there is no coin to hide
behind: BTC -$5,623 (PF 0.52, Sharpe -5.90, MaxDD -56.6%), ETH
-$3,875 (PF 0.69), HYPE -$3,017 (PF 0.75). Win rates 35–44% with
expectancy -$9.67 to -$16.44 a trade — the oversold bounces this
system buys either keep falling through the 2xATR stop or die
before RSI reaches 50, and the overbought fades get run over the
same way. Fees ($6,489) are large but not the explanation: every
coin's profit factor is below 1 before costs are even considered.

The percentile construction does what the paper promises — the zones
move with the regime — but on 1h crypto in this window the regime
moves faster than the 70-bar zones re-center, and RSI mean-reversion
at the 12th/88th percentile of its own recent distribution is not a
paying edge. The Bollinger variant (CALIBRATION.md) is worse
(-$16,253 combined), so the percentile version is the right one to
ship — it is just a losing one here.

## Mechanism

RSI(14) with adaptive zones: buy zone = 12th percentile of RSI over
rolling 70 bars, sell zone = 88th percentile. Long when RSI crosses
back above the buy zone after dipping below it; short when RSI
crosses back below the sell zone after exceeding it. Exits at RSI
crossing 50 or touching the opposite zone. 2xATR hard stop, 3xATR
chandelier trail, 120-bar max hold.

Sources: Dynamic Zones (Zamansky & Stendahl, S&C July 1996 V15:7) —
https://www.tradingview.com/script/AoChfBer-How-To-Use-Dynamic-Zones/
and https://docs.prorealalgos.com/dynamiczonersiup.html

## Limitations

- Single 7-month crypto window; 972 trades is a decent sample and
  all three legs agree, which is the honest signal here — this
  does not work on 1h crypto in this regime.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped percentiles on this window (see
  CALIBRATION.md — the 20/80 pair is less bad but still negative
  everywhere).
