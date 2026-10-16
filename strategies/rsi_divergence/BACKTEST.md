# RSI regular divergence — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → 2026-10-15
(BTC 5,157 bars; ETH 5,157; HYPE 5,155).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 1.5xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: Wilder RSI(14), 5-bar fractal pivots,
regular divergence + RSI<35/>65 at the second extreme, entry on the
30/70 re-cross within 20 bars, 1.5xATR stop, 2.5xATR trail, 72-bar
max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 5 | 20.0% | −$385 | −3.8% | −1.51 | −4.9% | −$76.98 | 0.31 |
| ETH | 9 | 11.1% | −$430 | −4.3% | −1.55 | −4.5% | −$47.77 | 0.39 |
| HYPE | 8 | 12.5% | −$589 | −5.9% | −2.48 | −6.4% | −$73.61 | 0.13 |
| **Combined** | **22** | **13.6%** | **−$1,404** | — | — | — | **−$63.82** | — |

## Verdict: too sparse to judge, and what fired lost

Twenty-two trades in seven months across three coins — the double
filter (divergence shape AND oversold RSI AND a fresh 30/70 re-cross)
is so strict on hourly data that the system barely participates. The
few trades it took lost at a 13.6% win rate, but with n=22 that is
noise, not a verdict on the idea.

Structural flaw worth naming: the 5-bar pivot confirmation lag eats
the entry. RSI usually re-crosses 30/70 *while the second pivot is
still being confirmed*, so by the time the divergence is "known" at
bar j+5 the confirmation already happened and the 20-bar pending
window opens onto a spent move. The stricter the confirmation
requirement, the more of the move it misses. Loosening the trigger to
40/60 roughly doubles trade count (10–22 per coin) but stays negative.

Hidden divergence (continuation setups) is not implemented here —
listed as an extension in signals.py. As shipped, this is a documented
negative/sparse result: the idea needs a same-bar confirmation design,
not a lagged one, before it deserves more capital.
