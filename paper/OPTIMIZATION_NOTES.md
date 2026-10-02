# Parameter + Coin Optimization — Hyperliquid Copy Engine (true-PnL)

Date: 2026-10-02. Script: `backtest_opt.py` (copy of `backtest_tuned.py` with env knobs
`OPT_TRAILING`, `OPT_TP`, `OPT_COIN_FILTER`; Kelly fixed at 0.25; `summarize()` extended
with `exit_mix` and `net_ex_top3`). Same 30d window and same 4 vaults for every run —
the window end was pinned via `OPT_TRADE_END_MS` so all variants replay the identical
fills/candles. Baseline reproduction (`smoke`: trailing 2%, TP 20%, all coins) matched the
K025 true-PnL run: +$214.77 / 3,716 / 55.6% WR (vs +$220.21 — window shifted minutes).

## Grid results (30d, $10k, Kelly 0.25, SL 8%, max-hold 24h)

| variant | trailing | TP | coin filter | net $ | trades | WR | fees $ | ex-top3 $ | exit mix (net $ / legs) |
|---|---|---|---|---|---|---|---|---|---|
| smoke (baseline) | 2.0% | 20% | all | +214.77 | 3,716 | 55.6% | 36.72 | +144.38 | trail +214/277 · stop −46/11 · wend +30/13 · maxhold +23/35 · texit −6/3380 |
| trail1 | **1.0%** | 20% | all | +279.35 | 3,521 | 54.7% | 44.94 | **+219.58** | trail +359/396 · stop −51/13 · maxhold −21/18 · texit −11/3081 |
| trail3 | 3.0% | 20% | all | +219.47 | 3,968 | 59.8% | 32.64 | +149.66 | trail +154/207 · texit +32/3690 · maxhold +43/48 |
| trail5 | 5.0% | 20% | all | +227.10 | 4,109 | 57.6% | 29.06 | +119.44 | maxhold +111/89 · tp +105/5 · texit +97/3879 · trail −38/109 |
| tp6 | 2.0% | 6% | all | +204.29 | 3,657 | 52.9% | 37.34 | +168.97 | tp +300/51 · trail −33/242 · stop −58/11 |
| tp8 | 2.0% | 8% | all | +202.54 | 3,666 | 54.9% | 36.92 | +155.23 | tp +198/27 · trail +67/259 |
| tp10 | 2.0% | 10% | all | +214.99 | 3,699 | 55.7% | 36.80 | +155.69 | tp +143/14 · trail +121/268 |
| nomajors | 2.0% | 20% | skip BTC/ETH/BNB/LINK/DOGE | +230.24 | 3,061 | 57.3% | 31.47 | +161.02 | trail +225/234 |
| altsonly | 2.0% | 20% | alts-only (13 coins) | +253.65 | 3,030 | 57.5% | 27.49 | +184.60 | trail +243/212 |
| combo_a | 1.0% | 20% | alts-only | +280.02 | 2,893 | 54.7% | 34.09 | +220.25 | trail +341/294 |
| combo_b | 1.0% | **6%** | alts-only | +266.49 | 2,886 | 53.8% | 34.32 | **+231.17** | tp +221/34 · trail +120/266 |

(exit reasons: trail = trailing stop, tp = take-profit, texit = target's own close,
stop = 8% SL, maxhold = 24h, wend = still open at window end, marked to market.)

alts-only set (derived from K025 baseline: net > +$3 AND ≥5 trades): PONS, SUI, VVV,
CASHCAT, LIT, ZEC, ENA, HYPE, UNI, AVAX, PUMP, XRP, TAO.

## Winner (by ex-top3 net, robustness first)

**trailing=1%, TP=6%, coin filter=alts_only** (`backtest_opt_combo_b_summary.json`):
+$266.49 net / 2,886 trades / 53.8% WR / $34.32 fees / **+$231.17 ex-top3**.

No thin-trade flags: every variant ran 2,800–4,100 trades.

## What the grid actually proved

1. **Trailing 1% is the big, robust win.** +$279/+220 vs baseline +$215/+144 — large
   margins on BOTH headline and ex-top3, 396 trailing legs (broad-based, not outliers).
   The vaults' edge is short-horizon: a tighter trail locks in the move before it fades.
   Wider trailing (3–5%) is no better than 2%; at 5% the trail goes quiet and exits
   degrade into max-hold drift (+$111/89 legs — luck, not edge).
2. **Alts-only filter is the second robust win.** +$254/+185 vs +$215/+144, and the
   filtered-out coins confirm the call: majors (BTC/ETH/BNB/LINK/DOGE) were flat to
   negative across 600+ baseline trades. Fee bill also drops ($27.49 vs $36.72).
3. **A reachable TP does NOT beat pure trailing at 2% width** — TP 6/8/10% all score
   ≤ baseline because the TP cannibalizes trailing exits (tp6: trail goes −$33/242).
   The TP only earns its place paired with the 1% trail: TP 6% banks +6% on runners
   *before* the tight trail gets wicked out by a 1% pullback (34 TP legs, +$221,
   avg +$6.50; exit verified at exactly entry×1.06).
4. **Gate still validated on the winner**: 2,393 skipped signals (gate rejects +
   filtered coins) net −$90.79 at 43.5% WR — the filter is avoiding real losers.

## Honest assessment: robust vs overfit

- **High confidence**: trailing 1% and the alts-only filter. Large effect sizes,
  consistent across headline PnL, ex-top3, and WR, with a clear mechanism.
- **Low confidence (marginal)**: the TP=6% component of the winner. It beats no-TP on
  ex-top3 by only +$11 (+231.17 vs +220.25) while *losing* headline by −$14 (+266.49
  vs +280.02). It was selected from 11 tested configs, so selection bias is real.
- **In-sample warning**: the alts-only coin set was derived from the K025 baseline on
  the SAME 30d window and SAME 4 vaults it was then tested on. The trailing grid is
  also single-window (4 width points; the true optimum could sit between or below
  1%). Nothing here is validated out-of-sample yet.
- **Methodology caveats**: full fills at historical prices, no market impact, exits on
  15m candles, no funding modeled, taker+slippage fees. `window_end` legs are
  unrealized marks, not realized PnL.

**Bottom line**: adopt trailing=1% + alts-only as the high-confidence core
(+$280/+220 on the combo_a run). Keep TP=6% as the stated winner per the ex-top3
rule, but treat it as provisional — the forward paper test (live, out-of-sample) is
the real judge, and if the TP doesn't confirm there, drop it back to TP=20%
(effectively trailing-only).

## Files

- `backtest_opt.py` — grid script (env: `OPT_NAME`, `OPT_TRAILING`, `OPT_TP`,
  `OPT_COIN_FILTER`, `OPT_TRADE_END_MS`)
- `backtest_opt_<name>_summary.json` — per-variant summaries: smoke, trail1, trail3,
  trail5, tp6, tp8, tp10, nomajors, altsonly, combo_a, combo_b
- `backtest_opt_<name>_trades.csv` / `backtest_opt_<name>.log` — per-variant legs/logs
- Untouched: `backtest.py`, `backtest_tuned.py`, all existing summaries/CSVs,
  `paper_tracker.*`. No cron jobs created.
