# Dual Thrust — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → 2026-10-10
(~5,030 bars each; API caps history at 5,000 candles/request).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled
(notes as limitation; max 24-bar holds keep it second-order).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: K1=K2=0.7 over 5 prior UTC-day sessions, reversing entries, 2xATR stop, 24-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 17 | 47.1% | +$393 | +3.9% | 0.91 | -4.0% | +$23.11 | 1.47 |
| ETH | 19 | 36.8% | +$1,034 | +10.3% | 1.41 | -6.2% | +$54.43 | 1.85 |
| HYPE | 14 | 57.1% | +$1,386 | +13.9% | 2.03 | -2.6% | +$98.97 | 3.70 |
| **Combined** | **50** | **46.0%** | **+$2,813** | — | — | — | +$56.25 | — |

## Verdict: WINNER

Positive on all three coins with positive Sharpe (0.91–2.03) and profit
factors 1.47–3.70. The session-range breakout survives contact with 1h
crypto data: the 5-session dual range sets wide enough lines that entries
only fire on genuine expansion days, and the reversing exit cuts
mean-reversion chop before the 24-bar hold expires. Fees ($336 combined)
are material but absorbed. HYPE is the star (profit factor 3.70) — its
wider intraday ranges fit the breakout sizing.

## Calibration note

Shipped the classic K=0.7 both sides without tuning first — the win is not
a fitted artifact. The K sweep (0.5/0.7/0.9, see CALIBRATION.md) confirms
0.7 sits in the stable region rather than on a knife edge. What I verified:
BuyLine/SellLine match the hand-computed formula exactly (unit test), and
indicators are lookahead-free by truncation test. What needs watching:
trade count is low (14–19 per coin over 7 months), so the Sharpe is
fragile — a handful of trades decides the verdict. The mechanism trades
expansion, not trend; in a sustained one-way melt the reversing exit will
give back open profit on every flip.

## Mechanism

Session = one UTC day of 1h bars. Range = max(HH-LC, HC-LL) over the 5
complete prior sessions. BuyLine = day open + 0.7*Range, SellLine = day
open - 0.7*Range. Long on close crossing above BuyLine, short on close
crossing below SellLine; reversing system (opposite entry closes the
position). 2xATR hard stop, no trailing/target, 24-bar max hold.

Source: Dual Thrust (Michael Chalek) — FMZ Quant implementation writeup —
https://steemit.com/fmz/@fmz.com/implementation-of-dual-thrust-trading-algorithm-by-using-mylanguage-on-fmz-quant-platform

## Limitations

- Single 7-month, choppy-to-bearish crypto window; no bull-market sample.
- Small trade counts (14–19 per coin): Sharpe/profit-factor estimates are noisy.
- Funding unmodeled (short book would earn it; longs would pay).
- Next-bar-open execution vs idealized breakout entry; breakout slippage not modeled beyond 0.01%.
- No daily-bar variant tested; crypto trades 24/7 so the "session" is a UTC-day fiction, though it works empirically.
