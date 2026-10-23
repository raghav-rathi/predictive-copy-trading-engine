# Breakout-Retest Throwback — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), sliced to `[1773446400000, 1792713599000)` (2026-03-14 00:00
UTC → 2026-10-23 23:59 UTC; actual data starts 2026-03-14 22:00
UTC for BTC/ETH, 2026-03-15 00:00 UTC for HYPE): 5,330 bars
BTC/ETH, 5,328 HYPE.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 1.0×ATR stop, 3×
leverage cap, $10k start, long + short. WARMUP=80 bars.

## Results (shipped config: 20-bar range, 20-bar retest window,
0.1/0.5 ATR touch/loss bands, clean-retest entries, level-loss
signal exits, 1.0×ATR stop, 2.0×ATR target, 96-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 173 | 30.1% | -$3,694 | -37.2% | -2.66 | -39.5% | -$21.35 | 0.68 |
| ETH | 160 | 33.1% | -$2,813 | -28.1% | -2.00 | -34.2% | -$17.58 | 0.74 |
| HYPE | 223 | 33.2% | -$2,071 | -20.7% | -1.26 | -33.4% | -$9.29 | 0.87 |
| **Combined** | **556** | **32.2%** | **-$8,578** | — | — | — | -$15.43 | — |

Fees: BTC $3,041, ETH $2,233, HYPE $2,243.

Long/short split: longs lose on every coin (BTC −$2,804, ETH
−$2,503, HYPE −$1,144; long win rates 26–33%); shorts lose less
but still lose (BTC −$890, ETH −$310, HYPE −$927; short win
rates 34–40%). Exit reasons: the 1.0×ATR hard stop takes ~64%
of trades (112/173 BTC, 98/160 ETH, 133/223 HYPE), the 2.0×ATR
target ~31%, the level-loss signal exit only ~7%.

## Verdict: a loser on all three coins — the throwback fails here

Combined −$8,578 across 556 trades, profit factors 0.68–0.87,
Sharpes −1.3 to −2.7. This is not fee-noise around zero; it is a
decisive rejection at the shipped settings.

The anatomy of the failure is visible in the exit mix. The
strategy's whole premise is "the retest holds," so the stop is
deliberately tight (1.0×ATR) under the retest level — but ~64%
of trades die on that stop. The polarity flip does not hold
often enough: with a 2R target the system needs >33% wins before
costs, and it delivers 30–33% with 0.055%/side costs. In other
words, at these a-priori bands the 1h crypto market does not
respect the broken 20-bar extreme as a polarity level often
enough to pay for the attempts. The longs are the worse side
everywhere (26–33% win rates), consistent with the window being
a grinding downtrend where throwback longs get run over.

What would NOT fix this: tightening the touch band (fewer,
pickier entries — the failure mode is the *hold*, not the
entry count), or widening the stop in-sample (that is fitting
to this window's noise). Any resurrection attempt — deeper
retest definition, higher-timeframe levels, HTF-trend filter so
retests only trade with the trend — belongs on walk-forward
data, not on this window.

## Mechanism

20-bar rolling extreme; breakout = close crosses the prior-bar
extreme; within the next 20 bars a clean retest = wick touches
`level ± 0.1×ATR` with no prior close beyond `level ∓ 0.5×ATR`
and the close rejects back across the line; exit on close
beyond `level ∓ 0.5×ATR` (level lost). 1.0×ATR stop, 2.0×ATR
target, 96-bar max hold, 1% risk, 3× leverage.

Sources: https://agentictrading.info/learn/what-is-a-breakout-retest.html —
https://daytradingtoolkit.com/strategies/breakout-retest-trading-strategy

## Limitations

- Single 7.3-month crypto window, 556 trades — thin and the
  window itself trends down, which flatters shorts and punishes
  the long side of a symmetric system.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- The 0.1/0.5 ATR bands and 20/20 lengths were never tuned —
  deliberately, to avoid in-sample selection (see
  CALIBRATION.md).
