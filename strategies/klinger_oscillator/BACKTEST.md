# Klinger Volume Oscillator — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-20 → 2026-10-14
(BTC 5,001 bars; ETH 5,001; HYPE 5,002).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2.5xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: VF = V·|2·(dm/cm)−1|·100·trend,
KVO = EMA(VF,34)−EMA(VF,55), 13-EMA signal, cross entries, exit on
opposite cross, 2.5xATR stop, 3xATR trail, 120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 609 | 29.9% | −$5,505 | −55.1% | −5.23 | −56.2% | −$9.09 | 0.62 |
| ETH | 603 | 31.8% | −$3,734 | −37.3% | −3.04 | −47.0% | −$6.29 | 0.75 |
| HYPE | 530 | 34.2% | −$732 | −7.3% | −0.41 | −13.9% | −$1.44 | 0.95 |
| **Combined** | **1,742** | **31.9%** | **−$9,971** | — | — | — | −$5.72 | — |

## Verdict: LOSER (killed — worst combined loss in the batch)

−$9,971 combined across 1,742 trades. The signal-line cross fires
constantly (609 BTC trades — a cross every ~8 bars) and every cross is
a coin flip with costs attached: 29.9% win rate on BTC with PF 0.62.
Volume force on 1h crypto is dominated by wash/chop volume, not the
accumulation/distribution flow Klinger designed it for on daily
equities. Even HYPE can't save it (−7.3%). Killed without a rescue
attempt — the signal is noise at this timeframe.

## Calibration note

Indicators verified: independent loop recomputation of VF matches the
module to 1e-9 past warmup; signal line verified as the exact 13-EMA of
KVO; truncation test proves lookahead-freedom. Mechanism quirk: the
dm/cm "temp" term assumes volume distributes across the bar range the
way 1990s equity volume did; on 1h perps, volume clusters at range
extremes during liquidations, which inverts the term's intent. If
revisited, use it only as a divergence filter on daily bars, never as
a 1h trigger.
