# Key reversal bar — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → 2026-10-15
(BTC 5,157 bars; ETH 5,157; HYPE 5,155).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: 20-bar key-reversal pattern, NO volume filter —
calibration tested 1.5x-volume confirmation and dropped it; entries on
pattern completion, exits on the opposite pattern, 2xATR stop, 3xATR
trail, 48-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 34 | 41.2% | −$310 | −3.1% | −0.46 | −13.3% | −$9.12 | 0.84 |
| ETH | 26 | 34.6% | +$1,263 | +12.6% | +1.79 | −7.0% | +$48.57 | 1.90 |
| HYPE | 43 | 39.5% | +$928 | +9.3% | +1.32 | −8.1% | +$21.58 | 1.37 |
| **Combined** | **103** | **38.8%** | **+$1,881** | — | — | — | **+$18.26** | — |

## Verdict: mixed-positive — ETH/HYPE work, BTC is flat-to-down

ETH is the standout (+12.6%, Sharpe +1.79, profit factor 1.90 on 26
trades); HYPE adds +9.3% at Sharpe +1.32. BTC is a mild loser (−3.1%).
The pattern fires rarely (26–43 trades per coin over 7 months), which is
correct for an exhaustion pattern — but it also means the ETH print
rests on a small sample and wants out-of-sample confirmation before any
weight. Combined +$1,881 is honest, not cherry-picked: the BTC loser is
in the table.

## Implementation notes (rules in my own words)

- Bearish key reversal: new 20-bar high AND close below the prior bar's
  low. Bullish: new 20-bar low AND close above the prior bar's high.
- The 1.5x average-volume confirmation was implemented, swept, and
  dropped — the unfiltered variant wins on all three coins (see
  CALIBRATION.md).
- Signal fires on the pattern bar's close; the harness executes at the
  next bar's open. Exits: the opposite pattern, plus stop/trail/max-hold.
