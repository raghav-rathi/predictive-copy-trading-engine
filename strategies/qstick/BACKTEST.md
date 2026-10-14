# Qstick — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-20 → 2026-10-14
(BTC 5,001 bars; ETH 5,001; HYPE 5,002).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: Qstick = SMA(8) of (close−open), zero-cross
entries, exit on opposite cross, 2xATR stop, 2.5xATR trail, 96-bar max
hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 877 | 23.7% | −$7,422 | −74.2% | −7.13 | −75.2% | −$8.49 | 0.56 |
| ETH | 888 | 25.5% | −$6,239 | −62.4% | −5.11 | −65.9% | −$7.08 | 0.64 |
| HYPE | 806 | 31.0% | −$4,085 | −40.9% | −2.97 | −43.8% | −$5.11 | 0.79 |
| **Combined** | **2,571** | **26.6%** | **−$17,746** | — | — | — | −$6.90 | — |

## Verdict: LOSER (killed — catastrophic)

−$17,746 combined, the worst single strategy in this batch by a wide
margin. The 8-bar body average whipsaws across zero constantly (877
BTC trades), and with a 23.7% win rate the math never had a chance.
Chande's Qstick quantifies candlestick bias fine as a *descriptor*,
but as a 1h *trigger* it is pure chop: the zero cross has no memory of
whether the bias is fresh or exhausted. Killed, no rescue.

## Calibration note

Indicators verified: Qstick and its trigger match independent rolling
means exactly; all-up-bodies test confirms sign behavior; truncation
test proves lookahead-freedom. Mechanism quirk: SMA(8) of bodies is
essentially an 8-bar net-drift meter — on 1h crypto, net drift over 8
bars is dominated by noise, so the cross is a noise trigger. The only
revisit path is using Qstick as a *filter* (e.g. require Qstick>0 for
long entries of a slower system) rather than a trigger.
