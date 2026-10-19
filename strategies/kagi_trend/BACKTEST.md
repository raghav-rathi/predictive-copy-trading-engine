# Kagi Yang/Yin Trend — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 00:00 UTC → 2026-10-19 13:00 UTC
(ms `[1773446400000, 1792414800000)`): 5,247 bars BTC/ETH, 5,245 HYPE
(HYPE history starts 2026-03-15 00:00 UTC).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=60 bars.

## Results (shipped config: close-based Kagi, reversal = 4xATR(14),
long on thin→thick (shoulder), short on thick→thin (waist), exits on the
opposite transition, 2xATR stop, 100-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 25 | 36.0% | +$3,371 | +33.5% | +2.70 | -5.0% | +$134.84 | 2.73 |
| ETH | 21 | 19.0% | -$444 | -4.4% | -0.51 | -10.2% | -$21.15 | 0.76 |
| HYPE | 23 | 21.7% | -$870 | -8.7% | -0.96 | -11.5% | -$37.82 | 0.51 |
| **Combined** | **69** | **26.1%** | **+$2,057** | — | — | — | +$29.81 | — |

## Verdict: mixed — a BTC-driven winner, losers elsewhere

The BTC book is a genuine trend-following profile: 36% win rate, fat
winners, profit factor 2.73, Sharpe +2.70, max drawdown only -5.0% on
25 trades. But ETH and HYPE both lose with profit factors of 0.76 and
0.51 and win rates under 22% — on their choppier 1h structure the
yang/yin transitions whipsaw: shoulders and waists print, then the move
fails and the 2xATR stop takes it. Combined +$2,057 is entirely the BTC
leg; the coin split says regime/asset-dependent, not robust. And 69
trades total is a thin sample for any "strategy works" claim. Fees
($531 combined) are not the story either way.

## Calibration note

Shipped the specified 4xATR reversal. A 2x/4x/6x reversal sweep is in
CALIBRATION.md: 2xATR is positive on all three coins (combined +$2,558,
most consistent); 6xATR is best combined (+$3,935, BTC PF 4.22) but
HYPE still loses. The reversal amount is a real sensitivity knob — keep
4x as specified, revisit with walk-forward evidence.

## Mechanism

Close-based Kagi chart: a column extends while closes keep moving the
same way; a reversal of ≥ 4xATR(14) starts a new column with a
horizontal step. The line thickens (yang) when a rising column's high
breaks the previous column's high ("shoulder") and thins (yin) when a
falling column's low breaks the previous column's low ("waist").
Long on the thin→thick transition, short on thick→thin; exits on the
opposite transition (the Kagi structure manages the trade). 2xATR hard
stop, 100-bar max hold.

Source: Kagi chart technique —
https://www.marketinout.com/technical_analysis.php?t=Kagi&id=56

## Limitations

- Single 7-month crypto window; 69 trades is a thin sample.
- BTC/ETH/HYPE split (works on BTC, fails on ETH/HYPE) — not robust
  across assets at the shipped setting.
- Kagi is built on closes, not highs/lows (documented choice: keeps
  the no-lookahead contract clean, since intrabar range is unknown at
  the close).
- 4xATR reversal is slow — catches big shoulders/waists, misses fast
  reversals and can give back open profit before the opposite
  transition prints.
- Funding unmodeled; next-bar-open execution vs idealized entry.
