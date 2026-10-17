# ICT liquidity-sweep (stop-hunt) reversal — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-23 → 2026-10-17
(BTC 5006 bars; ETH 5006; HYPE 5008).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the hard-stop distance, 3x leverage cap, $10k start.

## Results (shipped config: Wick >0.25 ATR through the 20-bar swing extreme with a close back inside: short the buy-side sweep, long the sell-side sweep; exit on opposite sweep or a closing break; 2.5xATR stop, 2xATR target, 48-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 200 | 54.0% | -2432 | -24.3% | -2.80 | -29.0% | -12.16 | 0.72 |
| ETH | 190 | 55.8% | -1487 | -14.9% | -1.69 | -17.2% | -7.82 | 0.82 |
| HYPE | 162 | 53.1% | -1722 | -17.2% | -2.04 | -18.6% | -10.63 | 0.74 |

## Verdict: LOSER (negative skew)

The tell is the win rate: 53-56% wins but -15% to -24% net. Fading sweeps wins the small battles (rejection works more than half the time) and loses the war: when the 'sweep' is actually a real breakout, the 2.5xATR stop takes a full loss while winners are capped at 2xATR. Classic negative skew -- the strategy is short the breakout tail it cannot distinguish from the hunt.

## Calibration note

Sweep detector verified on constructed bars: wick-through + close-inside fires, close-beyond does not (breakout, not a sweep), sub-0.25-ATR pokes are rejected. Breakout-close invalidation exits the faded position as designed.

## Mechanism

Wick >0.25 ATR through the 20-bar swing extreme with a close back inside: short the buy-side sweep, long the sell-side sweep; exit on opposite sweep or a closing break; 2.5xATR stop, 2xATR target, 48-bar max hold.

Source: ICT / SMC — Liquidity Sweep reversal mechanics —
https://liquidityscan.io/blog/liquidity-sweep-then-structure-shift-the-stop-hunt-to-reversal-sequence

## Limitations

- Single 7-month window; HYPE-specific edges may be regime-specific.
- Funding unmodeled.
- Next-bar-open execution; fast-turn signals can slip.
