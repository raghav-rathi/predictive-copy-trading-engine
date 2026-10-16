# episodic_thrust — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-20 → 2026-10-15
(BTC 5,157 bars; ETH 5,157; HYPE 5,155).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: 30-bar neglect base — range <= 4x ATR
(hourly adaptation; daily original ~= 1.2x) and base volume < 0.8x prior
30-bar volume; thrust = range >= 2x ATR, volume >= 2x 50-bar mean, close
in top 30% of bar, close above base high; long only; first-down-bar exit
after 3+ up bars; 2xATR stop, 3xATR trail, 30-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 5 | 0.0% | −$227 | −2.3% | −2.46 | −2.3% | −$45.33 | 0.00 |
| ETH | 2 | 100.0% | +$56 | +0.6% | +1.19 | −0.2% | +$28.03 | ∞ |
| HYPE | 1 | 100.0% | +$209 | +2.1% | +1.92 | −0.6% | +$209.50 | ∞ |
| **Combined** | **8** | **37.5%** | **+$38** | — | — | — | **+$4.75** | — |

## Verdict: too rare to evaluate — no edge demonstrated

Eight trades in seven months of hourly data: the setup is extremely
selective, which is faithful to the original (true episodic pivots are
rare), but it leaves nothing to evaluate. BTC's 5 trades all lost
(−$227); ETH/HYPE's 3 combined trades won (+$265) — a sample size that
proves nothing either way. Combined +$38 is noise. The proxy cannot
replicate Bonde's edge because the edge lives in the catalyst
(earnings surprises), which a volume/range filter only gestures at.
This is the proxy's result, not Bonde's — documented honestly as
inconclusive.
