# Six-bot trading desk (paper mode only)

An implementation of [@0xNevsky's "Grok Bot for Traders: The 6-Bot Desk I
Actually Run"](https://x.com/0xnevsky/status/2103406033062199578) — six bots
with written charters on one shared machine, short-only USDT perpetual
futures. **Paper mode only**, like the rest of this repo: the Gate emits
alerts, it never places orders, and `executor.py` raises `NotImplementedError`
by design.

## The loop

```
daily close ──> screener.py      BOT 1: three-candle flip detector
                    │ bearish flip (bullish = context only, never traded)
                    ▼
                cartographer.py  BOT 2: 4H Fair Value Gap ladder from the
                    │             anchor high to the current low, top-to-bottom;
                    │             partial wick test -> TESTED
                    ▼
                risk_officer.py  BOT 3: sizes from account/stop/risk% only.
                    │             Adds (0.5% risk) ONLY if the previous entry
                    │             is at breakeven. Never looks at charts.
                    ▼
                gate.py          BOT 4: emits the alert (coin, zone, entry,
                    │             stop, size, risk%, PRIME tag, chart data) as
                    │             a Telegram-style message. NEVER trades.
                    ▼
1H confirmation ──> entry at next 1H open (paper fill in backtest.py)
                    ▼
                exit_clerk.py    BOT 5: 4H intrabar stop at zone top; daily
                    │             close above anchor -> EXIT; NEUTRAL in profit
                    │             -> hold; flat 72h -> STALE; 1R -> breakeven
                    ▼
                auditor.py       BOT 6: journals every trade (entry, exit, fee,
                                  slippage on separate lines, result in R) +
                                  every SKIPPED alert; grades vs the locked
                                  go/no-go thresholds
```

`sixbot/DESK_RULES.md` is the single source of truth — every bot reads its
parameters from the LOCKED PARAMETERS block via `config.py`. The go/no-go
thresholds were fixed before the first backtest and are never tuned after.

## Quick start

```bash
# fetch candles (public Hyperliquid API; cached in sixbot/data/, gitignored)
python3 sixbot/data.py

# run the paper backtest (12 majors, ~7 months — see notes)
python3 sixbot/backtest.py --out sixbot/results

# inspect
column -s, -t sixbot/results/sixbot_trades.csv | less
```

No dependencies beyond the Python standard library.

## Backtest notes (2026-10-04 run)

- **Window:** 2026-03-10 → 2026-10-04 (~209 days). The task asked for 12
  months, but Hyperliquid's `candleSnapshot` only retains 1H candles back to
  2026-03-10 (verified: 1d/4h go back 12+ months, 1h/15m/30m do not). 1D/4H
  history before 2026-03-10 is still used for indicator lookback (anchors,
  FVG scan); only the traded walk is limited.
- **Basket:** BTC, ETH, SOL, HYPE, DOGE, XRP, BNB, ADA, AVAX, LINK, NEAR, ARB.
- **Costs:** 0.05% taker fee per side, 0.02% slippage per side (worsened).
- **Entries:** next 1H open after the confirming 1H close. **Stop:** zone top,
  no buffer (per charter). One position per coin; alerts auto-taken
  (TESTED_ZONE-flagged alerts included in the main ledger; the auditor
  reports the clean-vs-flagged split as "what SKIPPED would have done").
- **Result: NO-GO.** 46 trades (≥40 PASS), win rate 2.17% (≥33% FAIL),
  expectancy −0.96R (≥+0.40R FAIL), max drawdown 37.9% (≤20% FAIL).
  45 of 46 trades stopped out; the lone winner exited STALE at +0.22R.
  No coin was profitable; PRIME tags did not help (5.6% vs 0.0% win rate,
  both deeply negative expectancy). Full table in `results/BACKTEST_NOTES.md`.

## Assumptions (charter gaps, documented — none tuned to the data)

- `RISK_PCT_INITIAL = 1.0%` on a $10,000 paper account (the article's risk%
  was not visible in the post text available).
- PRIME bounce test: latest closed 4H candle green + above the 6-bar low.
- FVG quality filter: red displacement candle > 0.5× ATR(14).
- Alert zone = highest FRESH zone of the ladder; newer alerts supersede
  pending ones; alerts expire after 14 days.
- STALE exits at market (the charter says "flag"; the paper desk exits so
  dead capital is journaled).
- Adds trigger on 1H re-touch confirmations at the zone while at breakeven
  (max 2); new flip alerts on a coin with an open position are journaled
  `POSITION_ALREADY_OPEN`.
- Max drawdown on a daily mark-to-market equity curve.
