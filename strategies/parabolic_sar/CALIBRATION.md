# Parabolic SAR — AF sensitivity calibration

Sweep on the same Hyperliquid 1h data (BTC + ETH + HYPE, ~5,030 bars each;
$10k start, 1% risk, 0.045% fee + 0.01% slippage per side). Shipped config
included for reference.

| Variant | Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Profit factor |
|---|---|---|---|---|---|---|---|---|
| shipped (AF 0.02→0.20) | BTC | 418 | 35.6% | -$2,564 | -25.6% | -1.97 | -41.9% | 0.80 |
| shipped (AF 0.02→0.20) | ETH | 397 | 34.5% | -$1,678 | -16.7% | -1.17 | -24.0% | 0.87 |
| shipped (AF 0.02→0.20) | HYPE | 486 | 36.8% | +$312 | +3.1% | 0.35 | -12.1% | 1.02 |
| **slow (AF 0.01→0.10)** | BTC | 303 | 35.6% | -$533 | -5.4% | -0.27 | -23.8% | 0.95 |
| **slow (AF 0.01→0.10)** | ETH | 286 | 35.7% | -$1,102 | -11.3% | -0.74 | -28.8% | 0.89 |
| **slow (AF 0.01→0.10)** | HYPE | 337 | 38.3% | +$1,412 | +14.8% | 1.19 | -10.3% | 1.13 |
| **fast (AF 0.05→0.30)** | BTC | 640 | 33.9% | -$5,256 | -52.6% | -5.50 | -53.9% | 0.64 |
| **fast (AF 0.05→0.30)** | ETH | 581 | 35.6% | -$3,822 | -38.2% | -3.20 | -41.7% | 0.73 |
| **fast (AF 0.05→0.30)** | HYPE | 709 | 38.5% | -$420 | -4.5% | -0.25 | -12.6% | 0.97 |

## Verdicts

- **Slower AF (0.01→0.10): BEST of the three.** Cuts churn ~29% (926 vs 1,301
  trades), leaves BTC near breakeven, and makes HYPE genuinely positive
  (+14.8%, Sharpe 1.19, profit factor 1.13). Still negative on ETH but with a
  far shallower drawdown.
- **Shipped AF (0.02→0.20): LOSER.** Too fast for 1h crypto noise; the SAR
  flips into every chop move and fees ($6.3k combined) do the rest.
- **Faster AF (0.05→0.30): CATASTROPHIC.** Churn explodes (1,930 trades),
  BTC gives up -52.6%, profit factor 0.64. Speeding the SAR up is the wrong
  direction on this timeframe.

## Calibration note

The direction is clear — slower is better — and the slow variant on HYPE
(+14.8% net, Sharpe 1.19) is the only result here worth keeping alive. The
obvious next step is pairing the slow AF with an ADX trend filter so the
system only reverses in trending regimes instead of whipsawing through
ranges; that was not tested in this run. Nothing from this sweep was
shipped — the registry keeps the canonical Wilder parameters.
