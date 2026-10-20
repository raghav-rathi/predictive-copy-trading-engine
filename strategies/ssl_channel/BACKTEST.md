# SSL Channel — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 00:00 UTC → 2026-10-20 13:00 UTC
(ms `[1773446400000, 1792501200000)`): 5,271 bars BTC/ETH, 5,269 HYPE
(HYPE history starts 2026-03-15 00:00 UTC; BTC/ETH cache opens
2026-03-14 22:00 UTC).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=30 bars.

## Results (shipped config: SMA(High,10)/SMA(Low,10) channel, long on
flip to bullish, short on flip to bearish, exits on opposite flip,
2xATR stop, 200-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 432 | 26.2% | -$5,546 | -55.4% | -3.45 | -64.7% | -$12.84 | 0.63 |
| ETH | 434 | 29.7% | -$3,711 | -37.2% | -1.78 | -47.5% | -$8.55 | 0.78 |
| HYPE | 418 | 34.7% | -$827 | -8.2% | -0.26 | -24.0% | -$1.98 | 0.95 |
| **Combined** | **1,284** | **30.1%** | **-$10,083** | — | — | — | -$7.85 | 0.80 |

## Verdict: the batch's worst loser — the channel whipsaws on 1h crypto

A 10-bar SMA channel flips constantly on 1h structure: 432 trades on
BTC alone, a 26–35% win rate, and a BTC max drawdown of -64.7%. The
state machine holds between the lines, but the lines sit close enough
that every chop sequence flips the regime, and the 2xATR stop harvests
each false flip. Fees ($7,856 combined) are a real chunk of the
-$10,083 net — a hyperactive channel is a fee factory too. HYPE is the
only leg near breakeven (PF 0.95). 1,284 trades is the largest sample
of the batch — this is a high-confidence loser on this window, not
noise.

## Calibration note

Shipped the specified length 10. A 6/10/20 sweep is in
CALIBRATION.md: 6 is worst everywhere (602 BTC trades, -$13,776
combined); 20 is best combined (-$2,973) with a genuine single-coin
bright spot — HYPE +$2,636 (PF 1.18, Sharpe +1.33, 272 trades) — but
BTC/ETH still lose at every length. Keeping 10: the n=20 HYPE print is
in-sample single-coin evidence, not an adoptable setting.

## Mechanism

ssl_up = SMA(High,10), ssl_dn = SMA(Low,10). Regime is bullish when
close > ssl_up, bearish when close < ssl_dn, and the prior regime
persists between the lines. Long entry on the flip to bullish (close
crosses above the active SSL line), short entry on the flip to
bearish; exits are the opposite flip, so the channel itself manages
the trade. 2xATR hard stop, no trail, no target, 200-bar max hold.

Source: SSL Channel strategy (fmz.com) —
https://www.fmz.com/strategy/443990

## Limitations

- Single 7-month crypto window; the SSL was popularized on forex
  where trends persist longer between flips.
- 10-bar channel is far too fast for 1h crypto chop; the sweep shows
  slower is better, but no length fixes BTC/ETH.
- HYPE's near-breakeven is not a win, and the n=20 HYPE sub-result
  must not be promoted without out-of-sample evidence.
- Funding unmodeled; next-bar-open execution vs idealized entry.
