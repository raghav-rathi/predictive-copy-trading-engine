# Ehlers RVI cross — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → 2026-10-15
(BTC 5,157 bars; ETH 5,157; HYPE 5,155).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: RVI = SMA10 of (c-o)/(h-l), 1-2-2-1 signal
line, unfiltered RVI/signal crosses, 2xATR stop, no trail, 72-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 134 | 30.6% | +$1,232 | +16.1% | +0.89 | −35.7% | +$9.20 | 1.12 |
| ETH | 137 | 27.7% | −$901 | −4.1% | −0.02 | −36.3% | −$6.57 | 0.90 |
| HYPE | 148 | 23.0% | −$2,129 | −19.5% | −1.06 | −27.9% | −$14.39 | 0.80 |
| **Combined** | **419** | **27.0%** | **−$1,798** | — | — | — | **−$4.29** | — |

## Verdict: BTC prints small (+16.1%), ETH/HYPE drag it negative

The raw cross is a whipsaw machine — win rates in the 23–31% band with
max drawdowns of 28–36% say the signal line gets crossed constantly in
chop and the 2xATR stop does the bleeding. BTC ekes out +$1,232, but
that is one decent trend leg covering ~134 churned trades; it is not a
system you would run as-is.

The honest story is in the calibration: adding the minimum-separation
filter (|RVI − signal| > 0.02 at the cross) flips ETH from −$901 to
+$1,091 and trims the HYPE loss, taking the combined book from −$1,798
to +$1,108. The filter is the difference between a tradeable and an
untradeable version of this idea. Shipped config stays unfiltered per
the documented spec, but the filtered variant is the promotion
candidate pending walk-forward validation.
