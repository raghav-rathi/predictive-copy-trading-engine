# Original Turtle Rules — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 00:00 UTC → 2026-10-21 23:59 UTC
(ms `[1773446400000, 1792627199000)`; actual data starts 2026-03-14
22:00 UTC for BTC/ETH, 2026-03-15 00:00 UTC for HYPE): 5,301 bars
BTC/ETH, 5,299 HYPE.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2N stop, 3x leverage cap,
$10k start. WARMUP=120 bars.

## Results (shipped config: full S1+S2 original rules — 20-bar S1 entries
with the skip rule, 55-bar S2 failsafe, 10/20-bar exits, 2N stop, no
pyramiding)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 87 | 20.7% | -$350 | -3.5% | -0.05 | -24.1% | -$4.02 | 0.94 |
| ETH | 80 | 22.5% | +$130 | +1.3% | +0.22 | -19.9% | +$1.63 | 1.02 |
| HYPE | 87 | 28.7% | +$552 | +5.5% | +0.44 | -13.2% | +$6.35 | 1.10 |
| **Combined** | **254** | **24.0%** | **+$332** | — | — | — | +$1.31 | **1.02** |

## Verdict: breakeven noise, not a strategy

Combined **+$332 on 254 trades, profit factor 1.02, expectancy +$1.31
a trade** — that is a coin flip with costs, not an edge. The legs:

- **BTC is a loser** (-$350, PF 0.94, maxDD -24.1% — the deepest hole).
- **ETH is noise** (+$130, PF 1.02, expectancy +$1.63 — one trade
  decides the sign).
- **HYPE is the only green leg** (+$552, PF 1.10, Sharpe +0.44) and it
  is not green enough to matter.

The trade anatomy explains why: win rates of 21–29% are Turtle-normal
(the originals lost 60–70% of trades), but on 1h crypto the 2N stop
kills ~65% of all positions (BTC 56 of 87 exits were stops, ETH 54 of
80, HYPE 52 of 87) and the surviving trend legs are not outsized
enough to pay for the bleed. Fees ($1,998 combined) are 6x the net.

## Structural finding: on 1h bars this is not really System 1 anymore

The skip rule interacts badly with intraday bar frequency. On daily
bars, 20-day breakouts are rare, so skipping after a winner skips an
occasional signal. On 1h bars, 20-bar breakouts fire constantly — so
after the first winning S1 trade in each direction, *every subsequent
S1 signal in that direction is skipped forever* (no S1 trade ever
completes to reset the state), and the S2 failsafe takes over
permanently. The counts prove it: of 87 BTC trades only 9 were S1
(8 long, 1 short); ETH 7 of 80; HYPE 3 of 87. **Over 90% of all
entries are 55-bar-breakout / 20-bar-exit S2 trades.** The shipped
config is the original rules applied faithfully — but faithfully
applied to 1h bars, the "System 1 with skip rule" component
self-extinguishes and you are left trading a slow 55-bar breakout
system with a 2N stop. That is a finding about the adaptation, not a
bug in the implementation (the internal skip-rule simulator was
verified trade-for-trade against the harness on synthetic data).

## Mechanism

Donchian channels on 1h bars: 20-bar (S1 entry), 55-bar (S2 entry),
10-bar (S1 exit), 20-bar (S2 exit); N = ATR(20). S1 breakout entries
skipped when the previous completed S1 trade in the same direction
was a winner (tracked by an internal simulator mirroring the
harness's execution: next-open entries, 2N stop, channel exits).
S2 failsafe taken when flat and the last S1 signal was skipped. 2N
stop via RiskConfig; no trail, no target, no pyramiding (single unit).

Sources:

- The Original Turtle Trading Rules (Curtis Faith, 2003) —
  http://mql5.com/en/articles/23448
- https://relaxedtrader.com/original-turtle-trading-rules/

## Limitations

- Single 7-month crypto window; 254 trades, combined result is noise.
- ~65% stop-out rate; the 1h adaptation degenerates to S2-only (see
  above) — the skip rule as specified does not survive the
  daily→hourly translation.
- Funding unmodeled; next-bar-open execution vs the original's
  intraday breakout execution.
- Never tune the shipped rules on this window (see CALIBRATION.md).
