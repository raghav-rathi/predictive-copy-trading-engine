# Detrended Price Oscillator — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-20 → 2026-10-14
(BTC 5,001 bars; ETH 5,001; HYPE 5,002).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: DPO(21) = C − SMA(21) from 11 bars ago
(causal displacement); zero-cross entries; exit on opposite cross;
2xATR stop, 2.5xATR trail, 72-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 350 | 24.3% | −$3,468 | −34.7% | −2.66 | −39.2% | −$9.94 | 0.70 |
| ETH | 406 | 22.7% | −$2,740 | −27.4% | −1.95 | −39.1% | −$6.96 | 0.79 |
| HYPE | 350 | 27.7% | +$373 | +3.7% | +0.37 | −15.5% | +$0.91 | 1.02 |
| **Combined** | **1,106** | **24.8%** | **−$5,835** | — | — | — | −$5.28 | — |

## Verdict: LOSER (weak mixed — HYPE barely positive)

−$5,835 combined. The causal displacement (comparing today's close to
the trend estimate from 11 bars ago) makes DPO a lagged cycle gauge,
and the zero cross fires mid-swing on 1h crypto — entries arrive after
the cycle turn is half over, and the 24.8% win rate can't carry the
costs. HYPE's +3.7% is noise (Sharpe 0.37). The textbook DPO needs the
non-causal centered average to time cycles; the causal version is a
different, worse indicator. Honest conclusion: don't ship the causal
approximation as a trigger.

## Calibration note

Indicators verified: DPO matches the independent SMA-shift
recomputation exactly; sine-wave test confirms phase behavior;
truncation test proves lookahead-freedom (the whole point of the
causal form). Mechanism quirk worth stating plainly: causal DPO ≈ a
lagged momentum oscillator, not a cycle timer — the displacement that
makes textbook DPO useful is precisely the lookahead we removed.
Revisit path: use DPO only for cycle-length estimation (regime
context), never for entries.
