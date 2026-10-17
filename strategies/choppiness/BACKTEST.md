# Dreiss Choppiness-regime Donchian — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-23 → 2026-10-17
(BTC 5006 bars; ETH 5006; HYPE 5008).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the hard-stop distance, 3x leverage cap, $10k start.

## Results (shipped config: CHOP(14) regime filter (trend < 38.2, chop > 61.8); Donchian(20) breakouts only in trending regimes; exit on regime flip to chop or midline cross; 2xATR stop, 3xATR trail, 120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 72 | 36.1% | +618 | +6.2% | +0.70 | -13.2% | +8.58 | 1.15 |
| ETH | 101 | 23.8% | -2707 | -27.1% | -3.35 | -28.1% | -26.81 | 0.46 |
| HYPE | 70 | 41.4% | +690 | +6.9% | +0.81 | -6.9% | +9.85 | 1.21 |

## Verdict: MIXED (thin positive)

BTC +6.2% (Sharpe 0.70) and HYPE +6.9% (0.81) with only 70-72 trades: the regime gate does its job -- breakouts are taken only when the market is measurably trending, so the system sits out most chop. ETH -27.1% is the honest counterweight. DONCHIAN=30 sweep: BTC +1.4/HYPE +5.3 -- same shape, thinner. Small, fragile, but directionally the filter works.

## Calibration note

CHOP bounds verified [0,100]; straight trends score < 38.2, space-filling chop scores > 61.8. Breakout entries verified to never fire during choppy bars. Notable: on 1h crypto CHOP rarely exceeds 61.8, so the chop-exit seldom triggers -- exits come from the midline cross.

## Mechanism

CHOP(14) regime filter (trend < 38.2, chop > 61.8); Donchian(20) breakouts only in trending regimes; exit on regime flip to chop or midline cross; 2xATR stop, 3xATR trail, 120-bar max hold.

Source: E.W. Dreiss — Choppiness Index —
https://www.investopedia.com/terms/c/choppiness-index.asp

## Limitations

- Single 7-month window; HYPE-specific edges may be regime-specific.
- Funding unmodeled.
- Next-bar-open execution; fast-turn signals can slip.
