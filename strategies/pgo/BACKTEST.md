# Pretty Good Oscillator — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-20 → 2026-10-14
(BTC 5,001 bars; ETH 5,001; HYPE 5,002).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: PGO = (C − SMA(14)) / ATR(14); long on cross
above +1.0, short on cross below −1.0; exit on zero-line cross back;
2xATR stop, 3xATR trail, 96-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 311 | 29.3% | −$4,085 | −40.9% | −3.08 | −43.4% | −$13.16 | 0.65 |
| ETH | 294 | 31.3% | −$1,375 | −13.8% | −0.75 | −30.3% | −$4.74 | 0.89 |
| HYPE | 299 | 37.1% | +$675 | +6.8% | +0.54 | −16.6% | +$2.10 | 1.05 |
| **Combined** | **904** | **32.5%** | **−$4,785** | — | — | — | −$5.29 | — |

## Verdict: LOSER (weak mixed — best of the weak)

−$4,785 combined — the least-bad loser in the batch after Coppock.
The ±1.0 breakout entries catch real thrusts (37.1% win rate on HYPE,
the batch's best), but on BTC/ETH the thrusts reverse as often as
they extend, and the zero-line exit gives back the extension. HYPE
+6.8% at Sharpe 0.54 is the only positive print outside Coppock and
CMF/Elder/DPO noise. The mechanism is sound-ish; the timeframe is the
problem — 1h thrusts are mean-reverting more often than not.

## Calibration note

Indicators verified: PGO matches the independent (C−SMA)/ATR
recomputation exactly; steady-climb test confirms PGO>1 on sustained
thrusts; every long entry verified to cross +1.0 from below;
truncation test proves lookahead-freedom. Mechanism quirk: ATR in the
denominator is itself elevated during thrusts, which dampens the very
signal the numerator tries to catch — PGO understates the strongest
moves. Revisit path: asymmetric exits (trail the thrust instead of
exiting at zero) or run it on 4h bars where thrusts persist.
