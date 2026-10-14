# Chande Momentum Oscillator — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-20 → 2026-10-14
(BTC 5,001 bars; ETH 5,001; HYPE 5,002).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: CMO(14) = 100·(Su−Sd)/(Su+Sd); long on cross
above −50, short on cross below +50; exit on zero-line cross back;
2xATR stop, 2.5xATR trail, 96-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 153 | 36.6% | −$2,034 | −20.3% | −1.81 | −20.8% | −$13.30 | 0.70 |
| ETH | 151 | 37.7% | −$1,419 | −14.2% | −1.38 | −17.3% | −$9.40 | 0.76 |
| HYPE | 139 | 35.3% | −$2,270 | −22.7% | −2.59 | −26.8% | −$16.33 | 0.65 |
| **Combined** | **443** | **36.6%** | **−$5,723** | — | — | — | −$12.92 | — |

## Verdict: LOSER (killed)

Uniformly negative on all three coins — even HYPE, which usually bails
out momentum systems in this library, loses −22.7%. The ±50 extreme
crosses are rare (153 BTC trades in 7 months) and they mark momentum
that is already exhausted: entering as CMO leaves the extreme means
buying the tail of the burst. The zero-line exit then holds through
the full fade. Worst HYPE print in the batch relative to its trendiness
— this system's timing is inverted for 1h crypto.

## Calibration note

Indicators verified: independent Su/Sd recomputation matches exactly
(after fixing the test's bar-0 NaN convention); all-up-days = +100
confirmed; every long entry verified to cross −50 from below;
truncation test proves lookahead-freedom. Mechanism quirk: CMO's raw
sums make it jumpier than RSI, so the ±50 "extreme" is crossed by
single-bar spikes that immediately revert — the entry is really a
spike-chaser. Revisit path: smooth CMO with a 3-bar average before
applying the levels, or invert the system (fade the ±50 cross).
