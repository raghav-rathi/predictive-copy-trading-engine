# Dynamic Momentum Index — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, read from the
local cache only (`data/candles/{BTC,ETH,HYPE}_1h.csv`), pinned
batch-47 window ms `[1773525600000, 1795701600000)`
(2026-03-14 22:00 UTC → 2026-11-26 14:00 UTC exclusive, last
bar 13:00 UTC): 6,160 bars BTC/ETH, 6,158 HYPE (HYPE's first
bar is 2026-03-15 00:00 UTC). Funding not modeled (fully
offline run).
**Costs:** 0.045% taker fee + 0.01% slippage per side.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start per coin. WARMUP=40 bars.

## Results (shipped config: TD = clamp(int(14/Vi), 5, 30),
simple-mean RSI over TD; long on a cross up through 30,
short on a cross down through 70, exit on a cross back
through 50; 2xATR stop, 3xATR trail, 120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 347 | 36.3% | -$5,541 | -55.4% | -5.06 | -55.5% | -$15.97 | 0.49 |
| ETH | 336 | 43.5% | -$2,207 | -22.1% | -1.46 | -29.5% | -$6.57 | 0.82 |
| HYPE | 336 | 45.5% | -$2,124 | -21.1% | -1.31 | -29.6% | -$6.32 | 0.81 |
| **Combined** | **1,019** | **41.7%** | **-$9,873** | — | **-3.56** | **-35.5%** | **-$9.69** | **0.71** |

Fees: BTC $2,471, ETH $2,434, HYPE $1,374 (total $6,278).
Net % is the final-equity return (it includes the
mark-to-market of any position still open at the window end);
Net $ is the sum of closed-trade PnL.

## Verdict: a loser on every coin — the variable window does not save the oscillator

Combined -$9,873 on 1,019 trades (PF 0.71, Sharpe -3.56) is
the worst combined dollar loss of this batch's three
strategies. BTC is catastrophic (-$5,541, Sharpe -5.06,
MaxDD -55.5% — more than half the account), and ETH/HYPE
lose a fifth each (-$2,207 / -$2,124, PF 0.81–0.82). Signal
exits (183 / 192 / 192) only narrowly outnumber stop exits
(164 / 144 / 144), so roughly half of all trades end at the
2xATR stop: the 30/70 entries catch momentum after it has
already moved, and the 50-cross exit is too slow to keep
what the move gave. Win rates 36–46% with PF 0.49–0.82 say
the variable lookback adapts the window without adapting
the outcome — the DMI crosses are noise on 1h crypto.
Honest read: do not trade this. The Chande/Kroll idea is
faithfully implemented (see the audit in CALIBRATION.md),
and it loses anyway.

Note: ETH and HYPE both print 336 trades with identical
exit splits (192 signal / 144 stop). Verified as
coincidence, not a data bug: the two coins' raw signals
differ (ETH 280 long / 234 short entries, HYPE 275 / 277),
and the pinned driver reproduces both counts exactly.

## Mechanism

sd5 = stdev(close, 5); sd_avg = SMA(sd5, 10); Vi = sd5 /
sd_avg; TD = clamp(int(14 / Vi), 5, 30); DMI = RSI over the
last TD price changes, RS from simple means of gains/losses
(the definitional form, NOT Wilder smoothing — Wilder over a
changing window has no canonical definition). Long when DMI
crosses up through 30, short when it crosses down through
70, exit when it crosses back through 50. Flat stretches
give Vi undefined and DMI NaN (no volatility, no momentum
reading); an all-gain TD window reads 100, all-loss 0,
all-zero 50. The harness 2xATR hard stop / 3xATR chandelier
trail sit behind the 50-cross exit; 120-bar max hold.

Sources: Tushar Chande & Stanley Kroll — "The New Technical
Trader" (1994); S&C V.11:5 — https://www.luxalgo.com/library/concept/dynamic-momentum-index/
and https://docs.wickra.org/Indicators/Indicator-DynamicMomentumIndex

## Limitations

- Single ~8.4-month crypto window; the verdict is negative
  on all three coins, so no single-coin read generalises
  upward.
- ~1,019 trades on $6,278 of fees: the system trades far
  too often for an oscillator with PF 0.71.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped base period on this window.
