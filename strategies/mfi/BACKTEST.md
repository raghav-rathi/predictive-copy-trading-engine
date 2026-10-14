# Money Flow Index — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → 2026-10-12
(~5,080 bars each).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: MFI(14), 20/80 reversal entries, opposite-extreme exits, 2xATR stop, 168-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 115 | 35.7% | +$298 | +3.0% | 0.33 | -13.5% | +$2.59 | 1.04 |
| ETH | 147 | 33.3% | -$3,816 | -38.2% | -3.46 | -42.0% | -$25.96 | 0.57 |
| HYPE | 115 | 31.3% | -$2,252 | -22.0% | -1.92 | -27.9% | -$19.58 | 0.68 |
| **Combined** | **377** | **33.4%** | **-$5,770** | — | — | — | -$15.30 | — |

## Verdict: LOSER (BTC-only breakeven)

BTC ekes out +3.0% with a 0.33 Sharpe and a 1.04 profit factor — that is
breakeven after fees, not an edge. ETH and HYPE lose decisively
(-38%/-22%, Sharpe -3.5/-1.9). The MFI 20/80 reversal fades volume-backed
moves and on 1h crypto those moves keep running: the long exit at MFI 80
systematically cuts winners short while losers ride to the 2xATR stop.
Win rate 31–36% cannot support a profit factor below 0.7.

## Calibration note

Shipped the classic MFI(14)/20/80 without tuning — the BTC breakeven is
not a fitted artifact. The 10/90, 20/80, 30/70 sweep (see
CALIBRATION.md) shows no threshold choice rescuing ETH or HYPE; the
failure is structural (fading volume-backed momentum), not parametric.
What I verified: MFI = 100 exactly on all-up windows, 0 on all-down,
NaN on flat (no fake signals), hand-checked against the formula, and
lookahead-free by truncation test.

## Mechanism

Typical price TP = (H+L+C)/3, raw money flow = TP * volume; money ratio =
sum(positive flow, 14) / sum(negative flow, 14); MFI = 100 - 100/(1+MR).
Long on MFI crossing above 20 from below, short on crossing below 80 from
above; exit a long when MFI touches 80, a short when it touches 20.
2xATR hard stop, no trailing/target, 168-bar max hold.

Source: Money Flow Index (Gene Quong & Avrum Soudack, 1989) —
Investopedia — https://www.investopedia.com/terms/m/mfi.asp

## Limitations

- Single 7-month window; ETH/HYPE losses are too large to be a data artifact.
- Funding unmodeled.
- Daily-bar MFI (the timeframe most textbooks use) was not tested.
