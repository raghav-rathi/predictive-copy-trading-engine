# Connors RSI(2) Pullback (R3) — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → 2026-10-10
(~5,030 bars each; API caps history at 5,000 candles/request).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled
(notes as limitation; 1h-bar holds keep it second-order).
**Sizing:** 1% equity risk per trade on the 2.5xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: RSI(2)<10 after a 3-bar decline, close>SMA200; exit RSI(2)>70 or close<SMA50; mirror shorts; 2.5xATR stop, 30-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 191 | 45.6% | -$1,340 | -13.4% | -3.76 | -13.7% | -$7.01 | 0.51 |
| ETH | 207 | 45.9% | -$1,254 | -12.5% | -2.88 | -13.1% | -$6.06 | 0.59 |
| HYPE | 243 | 44.9% | -$1,079 | -10.8% | -2.78 | -11.2% | -$4.44 | 0.68 |
| **Combined** | **641** | **45.4%** | **-$3,673** | — | — | — | -$5.73 | — |

## Verdict: LOSER

Negative on all three coins with deeply negative Sharpe (win rate is a
respectable ~45%, but winners are cut before they can pay for the losers).
The exit combination — RSI(2)>70 to take profits plus close<SMA(50) as a
regime kill-switch — is the structural problem on 1h bars: in a strong
pullback the RSI(2) whips above 70 on the first relief bar and the trade
is gone before the real snapback, while the SMA(50) cut triggers mid-
consolidation on coins that then mean-revert anyway. Fees ($4.0k combined)
are material, but profit factor 0.51–0.68 means the gross edge is absent
even before costs. Connors' original R3 is a daily-bar, equity-market
play built on the opening-retracement structure of bull-market dips; the
1h crypto port trades a different regime where "pullback" is often the
first leg of a trend break rather than a bounce setup.

## Calibration note

Shipped exactly the specified parameters (RSI(2), 10/90 entry thresholds,
3-bar RSI streak, SMA200 trend filter, 70/30 exits, SMA50 regime filter,
2.5xATR stop, 30-bar max hold, no trailing/target) — the sweep in
CALIBRATION.md confirms the failure is structural, not parametric: a
looser threshold (5/95) and a tighter one (15/85) both lose, and a 2-bar
streak (which triples trade count) loses worse. What did survive contact
with data: entries genuinely fire only when all three conditions coincide
(unit-tested), and indicators are lookahead-free by truncation test.

## Mechanism

Trend filter (close vs SMA200) -> wait for RSI(2) to wash out (<10 after
3 consecutive down-bars in RSI for longs; >90 after 3 up-bars for shorts)
-> enter the pullback. Exit on RSI(2) reversal (>70 for longs, <30 for
shorts) or the SMA(50) regime break, with a 2.5xATR hard stop and a
30-bar max hold.

Source: Connors RSI2 Classic (Larry Connors) — MQL5 writeup —
https://www.MQL5.com/en/articles/17636

## Limitations

- Single 7-month, choppy-to-bearish crypto window; no bull-market sample.
- Funding unmodeled (short book would earn it; longs would pay).
- Next-bar-open execution vs idealized pullback-bar fill.
- Original R3 is a daily/equity-market system; the 1h-crypto port is an
  admitted regime transplant and the numbers show it.
