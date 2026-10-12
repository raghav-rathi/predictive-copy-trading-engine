# Woodies CCI — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → present
(BTC 5,080 bars; ETH 5,080; HYPE 5,078).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: classic CCI(14), hook ±100 within 20 bars, zero-line
cross entries, exit on CCI crossing back through 0, 2xATR stop, 48-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 391 | 21.7% | −$5,016 | −49.5% | −4.15 | −55.8% | −$12.83 | 0.61 |
| ETH | 403 | 22.3% | −$5,482 | −54.5% | −4.78 | −60.2% | −$13.60 | 0.57 |
| HYPE | 382 | 29.6% | +$1,886 | +19.9% | +1.22 | −15.2% | +$4.94 | 1.13 |
| **Combined** | **1,176** | **24.5%** | **−$8,612** | — | — | — | −$7.32 | — |

## Verdict: MIXED (leans loser)

HYPE is genuinely positive (Sharpe 1.22, PF 1.13 over 382 trades — not a
fluke count) while BTC and ETH are deep losers (−50%+ with Sharpe below
−4). The setup fires far too often on 1h BTC/ETH (~2.3 trades/day): the
±100 "extreme" on a 14-bar window is routine chop for hourly crypto, so
the hook filter barely filters. Fees tell the story: $3,210 on BTC alone
vs −$5,016 net. Combined book is −$8,612 — I ship the honest verdict, not
the HYPE cherry-pick. HYPE's edge is worth a follow-up (its wider hourly
ranges make ±100 a real extreme), not a portfolio allocation.

## Calibration note

Indicators verified: independent pure-Python loop recomputation matches
the pandas formula exactly; truncation test proves lookahead-freedom.
The sweep (see CALIBRATION.md) shows hook ±150 improves everything and
HYPE strengthens to Sharpe 1.91 — but BTC/ETH stay negative, so there is
no stable winning region to switch to; shipped the classic ±100.

## Mechanism

CCI(14) on typical price (h+l+c)/3 with Lambert's 0.015 constant. Long
when CCI crosses above 0 after printing below −100 within the last 20
bars (the Woodies hook); short on the mirror. Exit when CCI crosses back
through 0. 2xATR hard stop, no trail/target, 48-bar (2-day) max hold.

Source: Ken Wood — Woodies CCI system —
https://www.investopedia.com/terms/c/cci.asp

## Limitations

- Single 7-month window; HYPE's outperformance may be regime-specific
  (its intraday ranges widened in this window).
- 1,176 combined trades: the system over-trades by design at these
  parameters on 1h bars; fee sensitivity is extreme.
- Funding unmodeled.
- Next-bar-open execution vs the idealized zero-line cross fill.
