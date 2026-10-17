# Dean Malone Traders Dynamic Index — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-23 → 2026-10-17
(BTC 5006 bars; ETH 5006; HYPE 5008).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the hard-stop distance, 3x leverage cap, $10k start.

## Results (shipped config: RSI(13) green vs SMA(2) red crosses gated by SMA(34) yellow at 50; exit on the reverse cross or RSI 68/32; 2xATR stop, 3xATR trail, 96-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 1282 | 26.7% | -8360 | -83.6% | -12.95 | -83.6% | -6.52 | 0.47 |
| ETH | 1284 | 24.0% | -8208 | -82.1% | -12.19 | -82.1% | -6.39 | 0.45 |
| HYPE | 1277 | 28.7% | -7534 | -75.1% | -11.54 | -75.4% | -5.90 | 0.51 |

## Verdict: LOSER

The green/red cross fires ~1,280 times per coin: on 1h crypto the 2-bar signal line whipsaws through the RSI line constantly, and the 68/32 exits do not compensate. Win rates of 24-29% with 1,280 trades say the entries are anti-predictive at this timeframe. TDI is a regime overlay for discretionary FX swing trading; mechanized raw on hourly crypto it is a loss machine.

## Calibration note

Lines verified: red/yellow are exact SMAs of the green RSI line; band width is exactly 2x1.6185x the 34-bar std. Entry gate verified: every long entry has yellow > 50. The failure is the signal frequency, not the indicator math.

## Mechanism

RSI(13) green vs SMA(2) red crosses gated by SMA(34) yellow at 50; exit on the reverse cross or RSI 68/32; 2xATR stop, 3xATR trail, 96-bar max hold.

Source: Dean Malone — Traders Dynamic Index (CompassFX E.A.S.Y.) —
https://www.forexracer.com/traders-dynamic-index-tdi-indicator-mt4/

## Limitations

- Single 7-month window; HYPE-specific edges may be regime-specific.
- Funding unmodeled.
- Next-bar-open execution; fast-turn signals can slip.
