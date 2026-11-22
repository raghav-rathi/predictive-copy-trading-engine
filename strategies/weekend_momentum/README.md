# Weekend Crypto Momentum

Trade 168-hour momentum, but only on weekends: enter Friday
00:00 UTC, exit at the Monday 00:00 UTC bar, flat on weekdays.

## Mechanism

- **Momentum:** `mom168 = close[i] − close[i−168]` — 168 hourly
  bars is 7 days, so each hour is compared with the same hour last
  week.
- **Session:** derived from the bar's own UTC timestamp
  (`pd.to_datetime(df["t"], unit="ms", utc=True)`). The weekend
  session is Friday 00:00 UTC through Sunday 23:59 UTC
  (weekday ∈ {Fri, Sat, Sun}); `is_monday_open` marks the Monday
  00:00 UTC bar.
- **Long entry:** momentum > 0 on a weekend bar, while flat.
- **Short entry:** momentum < 0 on a weekend bar, while flat
  (the mirror).
- **Exit:** forced on the Monday 00:00 UTC bar. The harness
  executes at the next bar's open, so the exit lands at the Monday
  01:00 open — one hour later than the paper's Sunday 23:59 exit.
  That 1-hour slippage is a harness artifact, documented here, not
  a strategy choice.
- **One position per weekend.** The state machine takes exactly
  one entry per weekend session and does not re-enter after a
  mid-weekend stop-out. The paper's trade is a single weekend hold;
  re-entering after every stop would turn it into a churn of
  intra-weekend trades (see BACKTEST.md — the stateless variant
  was tested during development and lost ~55% per coin on exactly
  that churn).

## Honest flag: this is a contested anomaly

The source paper (ACR, 2020–Apr 2025, 10 majors) finds a weekend
momentum effect. Other 2026 studies find weekday return
differences are within noise and only weekend *volatility* is
robust. This backtest is a test of the anomaly, not a
confirmation of it — ranked accordingly, and the thin sample (35
trades per coin) means the result below should be read as
suggestive at most.

## Risk

2xATR stop, 2xATR chandelier trail, no fixed target, 72-bar max
hold (the length of a weekend session, a backstop for the Monday
exit), 1% risk per trade, 3x leverage cap. WARMUP = 192 bars
(168-bar momentum lag + one day of margin).

Source: Advances in Consumer Research, "The Weekend Effect in
Crypto Momentum"
(https://acr-journal.com/article/the-weekend-effect-in-crypto-momentum-does-momentum-change-when-markets-never-sleep--1514/).
