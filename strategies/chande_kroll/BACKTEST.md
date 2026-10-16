# Chande & Kroll Stop — Backtest

## Setup
- **Data:** cached Hyperliquid 1h candles, 5008 bars per coin (BTC, ETH), 5006 (HYPE);
  2026-03-14 → 2026-10-09 (~209 days). No network used.
- **Costs:** 0.045% taker fee + 0.01% slippage per side (harness defaults).
- **Sizing:** $10,000 starting equity, 1% risk per trade, max 3× leverage,
  6×ATR(14) loose hard stop, no trailing/target/max-hold in the harness —
  the Chande-Kroll lines themselves are the trailing stops. Funding disabled.
- **Execution:** signal on bar i close → filled at bar i+1 open. Warmup 80 bars.

## Results

| coin | trades | win% | net $ | net % | Sharpe | maxDD % | expectancy $ | profit factor |
|------|--------|------|-------|-------|--------|---------|--------------|---------------|
| BTC  | 226 | 33.2% | -1,134.32 | -11.34% | -2.99 | -13.21% | -5.02 | 0.63 |
| ETH  | 229 | 29.3% | -703.39 | -7.03% | -1.66 | -11.35% | -3.07 | 0.77 |
| HYPE | 243 | 33.3% | -665.45 | -6.65% | -1.79 | -6.92% | -2.74 | 0.77 |
| **combined** | **698** | — | **-2,503.16** | — | — | — | — | — |

## VERDICT: LOSER

Loses on all three coins, deeply negative Sharpes (-1.7 to -3.0), profit
factors 0.63–0.77. No spin: as a standalone entry system on 1h crypto, the
Chande-Kroll opposing-line cross does not work in this sample.

## Calibration note

The loss signature is the classic lagging-entry trap: the entry fires on a
cross of the *opposing* stop line, which by construction happens well after
the turn — the trade starts just as the easy part of the move is over, and
the SMA21 bias gate does not filter enough chop (win rates stuck near
30–33%). Trade frequency is high (~1.1 trades/day/coin, 698 total), so the
0.045%+0.01% per-side costs compound hard: $1,924 in total fees against
-$2,503 net PnL — costs explain most of the damage, but the gross edge is
negative too (profit factor < 0.8 everywhere), so this is not a "fees killed
a good system" story. Max drawdowns of 7–13% with no winning coin confirm it
is consistently wrong-footed, not merely unlucky. The honest calibration is
that the mechanism is at fault, not the parameters: p=10/q=9/x=1.5 are the
canonical Chande-Kroll values and retuning them will not fix a lagging
reversal entry. A fairer use of this indicator is as an *exit* engine — pair
the C-K trailing-stop lines with a faster, independent entry trigger instead
of trading the opposing-line cross.

## Mechanism summary

- `long_stop` = rolling 9-bar max of (10-bar highest high − 1.5 × ATR(10));
  `short_stop` = rolling 9-bar min of (10-bar lowest low + 1.5 × ATR(10)).
  Both lines shifted 1 bar (no lookahead); the q-window max/min locks the
  stops so they only tighten.
- Long entry: close crosses above `short_stop` AND close > SMA(21).
  Short entry: close crosses below `long_stop` AND close < SMA(21).
- Exits: cross of the *own* line (close below `long_stop` / above
  `short_stop`) — the lines are the trailing stops.

## Source

Tushar Chande & Stanley Kroll, *The New Technical Trader* (Chande Kroll
Stop). Reference: https://www.brokercheck.co.za/how-to-properly-use-the-chande-kroll-stop/

## Limitations

- Single regime: Mar–Oct 2026 was a choppy, breakdown-heavy crypto market;
  results may not generalize to strong trending regimes.
- 1h timeframe only; C-K was designed on daily bars.
- Canonical parameters (p=10, q=9, x=1.5) — no optimization attempted, and
  none is recommended (see calibration note).
- Funding excluded (`use_funding=False`); fills assumed at next bar open
  with fixed slippage, no market-impact modeling.
- Synthetic unit tests use fixed seeds chosen to exhibit the signal
  behavior deterministically (see test module docstring).
