# Morales & Kacher Buyable Gap-Up (BGU)

A Buyable Gap-Up is a gap-up on big volume in an uptrend (or a
constructive consolidation) where price holds above the gap day's
intraday low — the signature of institutional accumulation that
Morales & Kacher trade as a low-risk entry in *In the Buy Zone*.

## Rule (long)

```
open - prior close >= 0.75 x ATR(40)
volume >= 1.5 x the 50-day average volume
price above the 50-bar SMA and above the 200-bar SMA
```

- **Stop:** the gap bar's intraday low. A close below it means
  the gap failed — exit at the signal level (tracked in a state
  machine from the entry bar).
- **Exit:** also on a close below the 240-bar SMA — the 10-day
  moving-average violation. The original exits on the 10-day
  violation if the stock respected the 10-day for ≥ 7 weeks,
  otherwise on the 50-day violation; we simplify honestly to
  always the 10-day (240-bar) violation.
- **Short mirror (builder-added):** gap DOWN ≥ 0.75×ATR(40) below
  the prior close on high volume in a downtrend; stop is the gap
  bar's intraday high; also exits on a close above the 240-bar
  SMA.

## 1h scaling (documented)

- 50-day average volume = 1,200 bars on 1h.
- 10-day moving average = 240 bars; 50-day = 1,200 bars.
- The ATR(40) gap threshold and the volume average are both
  measured through the PRIOR bar, so the gap is judged on
  information available at the open.

## Honest flag: crypto has no overnight gap

Crypto trades 24/7, so the 1h open is normally within a tick of
the prior close — there is no true overnight gap. The 1h
open-vs-prior-close gap is the adaptation, and qualifying gaps
(≥ 0.75×ATR(40) in a single hourly open) will be much smaller
and rarer than equity overnight gaps. Expect few triggers; a
near-zero trade count is the honest outcome of the adaptation,
not a bug. See BACKTEST.md.

## Risk

2×ATR(14) harness stop as a backstop (the signal-level gap-low
exit is the real stop), no trail, no target, 240-bar (~10-day)
max hold, 1% risk per trade, 3× leverage cap. WARMUP = 1,250
bars (1,200-bar volume average + margin).

Source: MaxMarkets, "Morales and Kacher Buyable Gap-Up"
(Morales & Kacher, *In the Buy Zone*)
(https://maxmarkets.app/learn/strategies/morales_kacher_bgu).
