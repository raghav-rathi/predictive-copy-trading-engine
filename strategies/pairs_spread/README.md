# Pairs Spread (BTC-ETH)

Gatev, Goetzmann & Rouwenhorst's pairs trading (*Pairs Trading:
Performance of a Relative-Value Arbitrage Rule*, Review of
Financial Studies, 2006): find two assets whose prices move
together, trade the spread between them — buy the spread when it
is unusually cheap relative to its history, sell it when it is
unusually rich, exit when it mean-reverts.

## Rules

- **Spread:** log(BTC close) − beta × log(ETH close), where beta
  is the rolling 500-bar OLS hedge ratio, recomputed every bar
  from the trailing 500 bars only (fully causal).
- **z-score:** z = (spread − 100-bar mean) / 100-bar std of the
  log-spread.
- **Long the spread** (long BTC / short ETH) when z crosses
  below −2.
- **Short the spread** (short BTC / long ETH) when z crosses
  above +2.
- **Exit** when z crosses back through 0.
- The traded instrument is a single synthetic spread book: USD
  spread OHLC = BTC o/h/l/c − beta × ETH o/h/l/c, volume = BTC
  volume. The harness risk layer's 2xATR stop / 2.5xATR trail
  also applies; max hold 120 bars.
- Parameters are the GGR conventions (±2 entry, 0 exit) with the
  lookbacks set per the spec; nothing was tuned to this window.

All computation is causal, so signals on bar i use only data
through bar i's close.

## Source

- Gatev, Goetzmann & Rouwenhorst, "Pairs Trading: Performance of
  a Relative-Value Arbitrage Rule", *Review of Financial Studies*
  19(3), 2006: https://doi.org/10.1093/rfs/hhj020

Paper only, no live execution.
