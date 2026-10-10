# Chandelier Exit — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → 2026-10-09
(~5,030 bars each; API caps history at 5,000 candles/request).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled
(notes as limitation; 1h-bar holds keep it second-order).
**Sizing:** 1% equity risk per trade on the 2xATR(14) safety stop, 3x leverage cap, $10k start.

## Results (shipped config: 22-bar HH/LL breakout entries, chandelier exit HH22−3×ATR22 / LL22+3×ATR22, 2×ATR safety stop, no trail/target/max-hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 151 | 31.1% | -$2,182 | -21.8% | -1.43 | -28.5% | -$14.45 | 0.75 |
| ETH | 136 | 32.4% | -$342 | -3.4% | -0.06 | -18.7% | -$2.52 | 0.96 |
| HYPE | 139 | 35.3% | +$1,767 | +17.0% | +1.06 | -14.5% | +$12.71 | 1.21 |
| **Combined** | **426** | **33.0%** | **-$757** | — | — | — | -$1.78 | — |

## Verdict: MIXED — HYPE winner, BTC loser, ETH flat

Coin-split is the story. On HYPE the classic LeBeau system works as
advertised: breakout entries catch the exchange-token's trending
personality, the 3xATR chandelier gives winners room, Sharpe 1.06 and
profit factor 1.21 with ~$1.8k net on a $10k account. On BTC the same
mechanism bleeds: 22-bar breakouts on BTC 1h are fake-outs far more
often than trend starts in this window (PF 0.75, −$2.2k). ETH sits in
between, essentially a coin toss after fees (PF 0.96). The multiplier
sweep (CALIBRATION.md) shows BTC loses at every setting, so this is a
regime/coin property, not a mis-parameterization.

## Calibration note

Shipped exactly the specified classic parameters (ATR(22), 22-bar lookback,
3.0× multiplier — the textbook LeBeau values), then ran a robustness sweep
at 2.5 and 3.5. The sweep is honest about its limits: 3.0 is the best on
HYPE and ETH alike, but BTC is negative under all three, and the
combined PnL stays negative. Nothing in the sweep argues for changing the
textbook values; what argues for the strategy at all is the HYPE column.
A coin-filter variant (run it only on HYPE, or on coins with a positive
trend-personality) is the natural next iteration. What I verified instead
of more sweeping: the chandelier line equals HH22−3×ATR22 to 1e-8 on
hand-built data (unit test), entries fire exactly on the cross above the
prior 22-bar high, and the indicators are lookahead-free by truncation
test.

## Mechanism

Breakout entry on the 22-bar high/low (close crossing above the highest
high / below the lowest low of the prior 22 bars, excluding the current
bar). Exit at the chandelier line: HH22−3×ATR22 for longs,
LL22+3×ATR22 for shorts — the classic hanging stop that trails only in
the direction of the trade. 2×ATR(14) hard safety stop, no target, no
max hold.

Source: Chandelier Exit (Chuck LeBeau) — tradingview-strategies README —
https://github.com/eternahybridexchange/tradingview-strategies/blob/HEAD/strategies/trend-following/chandelier-exit/README.md

## Limitations

- Single 7-month, choppy-to-bearish crypto window; no bull-market sample.
- Funding unmodeled (short book would earn it; longs would pay).
- Next-bar-open execution vs idealized breakout entry; 22-bar breakout
  entries suffer most from slippage — the recorded slippage may be light.
- Only one coin (HYPE) shows real edge; BTC is a structural loser here.
