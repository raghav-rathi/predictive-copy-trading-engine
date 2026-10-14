# Dual-Bear Pullback Short — Backtest

**Data:** Hyperliquid `candleSnapshot` 1h bars, BTC + ETH + HYPE,
2026-03-14 → 2026-10-10 (~5,080 bars each). 1h bars are resampled to
daily and 4h inside the indicators (forward-filled onto the 1h index;
complete-period series are shifted one period — no lookahead).
**Costs:** 0.045% taker fee + 0.01% slippage per side; funding accrued
hourly from real fundingHistory (shorts collect positive funding).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. Warmup 1,500 bars (~62 days, for daily EMA55).

## Results (shipped config: author spec — daily EMA21<EMA55 + developing
close<EMA55 + daily vol≥20d SMA gate; two consecutive 4H bear bars with
the trigger bar closing within 0.5xATR(14, 1h) below 4H EMA21 and 4H
volume > 20-bar SMA; exit on 4H EMA21 reclaim; 2xATR hard stop; 240-bar
backstop; short-only)

| Coin | Signals | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|---|
| BTC | 0 | 0 | — | $0 | 0.0% | — | — | — | — |
| ETH | 1 | 1 | 0% | −$12 | −0.1% | −1.57 | −0.1% | −$12.25 | 0.00 |
| HYPE | 0 | 0 | — | $0 | 0.0% | — | — | — | — |
| **Combined** | **1** | **1** | **0%** | **−$12** | — | — | — | −$12.25 | — |

## Verdict: PORT FAILURE (no-signal)

The gate conjunction as specified fires ~0–1 times per coin over 7
months on Hyperliquid 1h data — there is no trade sample to validate
against. Gate autopsy on BTC (1,271 new-4H-block bars): daily regime
holds 14%, two-bear 22%, but the pullback gate (trigger bar within
0.5xATR(1h) below 4H EMA21) passes only 5.9%, and the intersection with
the 4H volume gate leaves zero entries. The author's OKX study reports
52 trades over 7 years (~0.6/month); pro-rata my window should show ~4
trades on BTC, so the port is roughly an order of magnitude too
selective — the author's effective trigger was looser than the spec's
"0.5xATR" reads on this venue (possibly a different ATR timeframe in the
original code). The CALIBRATION.md sweep shows loosening the pullback
does not reveal a robust edge either.

This is not a tradable verdict in either direction: I can neither
confirm nor deny the author's PF-1.64 claim from this port. Do not
trade it on these parameters.

## Calibration note

Shipped the author's 0.5xATR pullback (1h ATR(14), consistent with the
harness's 2xATR(1h) hard stop). The pullback sweep {0.5, 1.0, 2.0}
(same data/costs/sizing; throwaway `/tmp/dbs_sweep.py`): 0.5x → 1
trade (−$12); 1.0x → 2 trades (−$122); 2.0x → 11 trades (+$429, driven
by 6 ETH trades at PF 3.77 — noise at that count, BTC 0W–4L). Loosening
doesn't uncover a stable edge; it just admits noise. What I verified:
the 1h→daily/4h resample is lookahead-free by truncation test, entries
fire only on new-4H-block bars with all five gates green (synthetic
end-to-end test), the EMA21-reclaim exit logic is exact, and longs are
never generated. What would be needed to fairly evaluate the author's
claim: the original code's ATR timeframe for the pullback gate, or a
multi-year HL sample where the strict gate can accumulate trades.

## Mechanism

Short-only. Daily regime gate: daily EMA21 < EMA55, developing daily
close < EMA55, last complete day's volume ≥ 20-day SMA. Entry (first 1h
bar of each new 4H block): two consecutive complete 4H bear bars, the
trigger bar pulling back to within 0.5xATR(14) below 4H EMA21, trigger
4H volume > 20-period SMA. Exit: 4H close reclaims 4H EMA21 (the study's
key finding — exits drive the edge), 2xATR hard stop, 240-bar backstop.

Source: Dual-Bear Pullback Short — zhangyong78 BTC EMA short research —
https://github.com/zhangyong78/qqokx/blob/HEAD/btc_ema_short_research/results_v3_exit_study/research_report.md

## Limitations

- One trade in 7 months: no statistical statement is possible.
- The 0.5xATR pullback may misread the author's ATR timeframe; the
  original repo's exact trigger code would settle it.
- Single 7-month window; daily EMA55 needs 55 days, so the effective
  evaluation window is ~5 months.
- Next-bar-open execution; the reclaim exit is evaluated on developing
  4H values (lookahead-free, but noisier than a confirmed 4H close).
