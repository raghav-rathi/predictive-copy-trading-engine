# MACD Zero Cross — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`), filtered to t >= 1773525600000:
BTC/ETH 5,445 bars, 2026-03-14 22:00 UTC → 2026-10-27 13:00 UTC;
HYPE 5,443 bars, 2026-03-15 00:00 UTC → 2026-10-27 13:00 UTC.
**Window:** 2026-03-14 → 2026-10-27, Hyperliquid 1h, $10k, 1% risk, 3x cap, 0.045% fee + 0.01% slippage/side, funding off.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage
cap, $10k start, long/short. Funding not modeled (fully offline run).

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 187 | 31.0% | -1,745 | -17.5% | -1.38 | -24.9% | -9.33 | 0.78 |
| ETH | 211 | 31.8% | -237 | -2.4% | -0.04 | -25.3% | -1.12 | 0.98 |
| HYPE | 174 | 36.8% | +760 | +7.6% | +0.63 | -9.8% | +4.37 | 1.09 |
| **Combined** | **572** | — | **-1,222** | — | — | — | **-2.14** | — |

Total fees: $4,995.

## Verdict

LOSER. Combined −$1,222 across 572 trades (−$2.14 expectancy). The least-bad strategy in this batch — HYPE is mildly green and the drawdowns are the shallowest here — but BTC (−$1,745, Sharpe −1.38) and ETH (−$237) both lose, and a 31–37% win rate with profit factors under 1.09 on every leg is not a tradable edge. The zero cross is a trend filter, not a timing signal, and on 1h crypto it pays for that lateness in chop.
