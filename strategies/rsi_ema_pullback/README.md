# RSI pullback to EMA(50)

The classic pullback trade (Connors/Raschke lineage, *Street
Smarts*, 1995): in an uptrend, wait for the oscillator to dip
into oversold territory, then buy the recovery — never buy the
dip itself, buy the turn back up.

## Rule (long)

```
Trend:  close > EMA(50) AND EMA(50) rising
Arm:    RSI(14) dips below 40 (while the trend holds)
Entry:  RSI(14) crosses back above 40 (trend still holds)
Exit:   RSI(14) reaches 70, OR close below EMA(50)
```

- **Short mirror:** downtrend (close below a falling EMA(50)),
  RSI rises above 60, then crosses back below 60; exit on RSI
  30 or close above EMA(50).
- **No opposite-side flip:** a short setup firing while long
  does not flip the position — the long's own exits decide.

## 1h scaling (documented)

- *Street Smarts* is written for daily bars. On 1h bars the
  EMA(50) is a ~2-day average, far more sensitive to a single
  pullback than a 50-day EMA — so a dip deep enough to push
  RSI below 40 usually breaks the EMA first and voids the
  setup. Expect very few triggers on 1h crypto (3 trades in
  eight months in the backtest; HYPE had none).

## Honest flag: this is dip-buying, and the EMA filter is the only thing separating it from a falling knife

Buying an RSI dip in a downtrend is catching a falling knife.
The entire safety of this system is the EMA(50) trend filter:
the dip only counts if the uptrend is intact when RSI
recovers. The backtest shows the filter working almost too
well — it screens out nearly every setup along with the knives.
That is the system working as specified, not a bug to fix by
loosening the rules.

## Risk

2×ATR(14) harness stop as a backstop (the RSI 70/30 and EMA
exits are the real exits), no trail, no target, 120-bar
(~5-day) max hold, 1% risk per trade, 3× leverage cap.
WARMUP = 60 bars.

Source: Larry Connors & Linda Raschke, *Street Smarts* (1995),
pullback chapter — https://www.tradingview.com/ideas/
(reference only; implemented from the rules above).
