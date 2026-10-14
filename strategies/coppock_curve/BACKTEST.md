# Coppock Curve — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-20 → 2026-10-14
(BTC 5,001 bars; ETH 5,001; HYPE 5,002).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: WMA(10) of ROC(14)+ROC(11), zero-cross entries,
exit on opposite cross, 2xATR stop, 3xATR trail, 720-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 247 | 30.4% | −$2,144 | −21.4% | −1.43 | −31.6% | −$8.73 | 0.80 |
| ETH | 259 | 30.5% | −$1,409 | −14.1% | −0.83 | −24.3% | −$5.83 | 0.87 |
| HYPE | 220 | 39.1% | +$5,015 | +50.2% | +2.61 | −11.3% | +$22.70 | 1.37 |
| **Combined** | **726** | **33.1%** | **+$1,462** | — | — | — | +$2.01 | — |

## Verdict: WINNER on HYPE, loser on BTC/ETH (regime-dependent)

HYPE prints +50.2% at Sharpe 2.61 with a 39.1% win rate — the slow
zero-cross regime system rides HYPE's 2026 trending phases cleanly and
the 30-day max hold lets winners run. BTC/ETH lose a combined −$3,553:
the same slow crosses whipsaw through their 1h chop, entering months
late and exiting into noise. Combined +$1,462 only because HYPE's win
is bigger than both majors' losses. Honest read: this is a
HYPE-regime system, not a general one.

## Calibration note

Indicators verified: independent WMA-of-ROCs recomputation matches to
1e-9; warmup NaNs confirmed through bar 23; truncation test proves
lookahead-freedom. Mechanism quirk: on 1h bars the "long-term" Coppock
is really a ~2-week momentum gauge, not the monthly original — the
zero cross is a regime flip, not a bottom call. Next experiment worth
running: gate entries on the curve's slope (rising into the cross)
instead of the cross alone, to cut the late entries that bled on
BTC/ETH.
