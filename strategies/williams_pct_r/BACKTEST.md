# williams_pct_r — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-20 → 2026-10-15
(BTC 5,157 bars; ETH 5,157; HYPE 5,155).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: Williams' published trigger — %R touches
-100 (0), 5 bars pass, then %R crosses above -85 (below -15); exits at
%R > -20 (< -80); 2xATR stop, no trail, 48-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 217 | 47.5% | −$4,091 | −40.9% | −4.11 | −41.2% | −$18.85 | 0.59 |
| ETH | 295 | 45.8% | −$4,278 | −43.1% | −3.82 | −46.5% | −$14.50 | 0.68 |
| HYPE | 378 | 48.7% | −$4,832 | −48.3% | −4.42 | −50.5% | −$12.78 | 0.67 |
| **Combined** | **890** | **47.4%** | **−$13,201** | — | — | — | **−$14.83** | — |

## Verdict: the batch's worst — a systematic loser on all three coins

Williams' %R trigger is a 1979 daily-commodities mean-reversion rule,
and on 2026 hourly crypto it is a systematic loser: −40% to −48% on
every coin, Sharpe below −3.8 everywhere, 890 trades of evidence. The
mechanism fails because %R pins at −100 (0) for long stretches in
trending hourly markets — the "extreme" is not extreme, it's the regime —
so the 5-bar wait plus −85 cross fires into the middle of one-way
tapes, and the −20/−80 exits cut winners while the 2xATR stop absorbs
the full trend move. This is not a calibration problem (see
CALIBRATION.md): the trigger itself is wrong for this market. Kept in
the library as a documented anti-signal.
