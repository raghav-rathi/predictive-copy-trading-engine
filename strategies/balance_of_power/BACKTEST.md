# Balance of Power — Backtest

**Data:** local cache CSVs (`data/candles/{BTC,ETH,HYPE}_1h.csv`,
columns t,o,h,l,c,v; t in ms), sliced to the batch window
ms `[1773446400000, 1792627199000)` — 2026-03-14 00:00 UTC →
2026-10-21 23:59:59 UTC: 5,301 bars BTC/ETH, 5,299 HYPE
(data starts 2026-03-14 22:00 UTC for BTC/ETH, 2026-03-15 00:00 UTC
for HYPE). Fully offline; no API calls.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=30 bars.

## Results (shipped config: bop=SMA(raw_bop, 14), long on a cross above
zero, short on a cross below zero, exits on the opposite cross,
2xATR stop, 2.5xATR trail, 150-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 807 | 22.4% | -$7,236 | -72.4% | -6.97 | -74.0% | -$8.97 | 0.57 |
| ETH | 769 | 25.4% | -$5,242 | -52.4% | -3.85 | -57.0% | -$6.82 | 0.72 |
| HYPE | 688 | 31.0% | -$2,663 | -26.7% | -1.71 | -33.3% | -$3.87 | 0.86 |
| **Combined** | **2,264** | **26.0%** | **-$15,141** | — | — | — | -$6.69 | — |

## Verdict: a loser — zero-crosses are late and get chewed up by fees

Combined -$15,141 across 2,264 trades, and every leg is red. The
honest read is that a zero-cross of a 14-bar-smoothed BOP is simply
too slow a trigger for 1h crypto: by the time control has "shifted"
enough to cross zero, the leg is mid-move or already reversing, so
entries buy the top of control swings and the 2xATR stop takes them
off again at a loss. Win rates of 22–31% with profit factors below
0.9 across the board say this isn't bad luck — it's a structurally
losing trigger.

- **BTC is a disaster** (-$7,236, PF 0.57, Sharpe -6.97, MaxDD -74%).
  Fees alone ($5,453) consumed three-quarters of the damage — 807
  whipsaw trades is the wrong pace for a regime indicator.
- **ETH is a loser** (-$5,242, PF 0.72, Sharpe -3.85). Fees ($5,140)
  are effectively the whole net loss.
- **HYPE is the least-bad leg** (-$2,663, PF 0.86, Sharpe -1.71,
  31.0% win rate) — still red. The one setting where BOP's slow
  control read almost keeps up is the one coin that trends cleanly.

This one stays in the honest-loser bucket. The mechanism idea —
who won each bar, normalized by range — is sound as a regime *filter*,
but as a standalone entry trigger on 1h bars it is too late, too
noisy around zero, and pays the fee man on 2,264 trades. If BOP is
used at all in the future, it should be as a long/short bias filter
for another strategy's entries, never as the cross itself.

## Calibration note

Shipped the specified n=14. A 7/14/28 SMA-length sweep is in
CALIBRATION.md: every setting is negative on all three coins, so the
length choice changes only how much money is lost — n=14 was kept
because it was fixed a priori, not because it wins anywhere.

## Mechanism

Balance of Power (Igor Livshin, S&C Aug 2001): raw_bop =
(close − open) / (high − low) in [-1, +1] per bar (0.0 on a flat
bar), bop = SMA(raw_bop, 14). Long when bop crosses above zero
(buyers take control); short when it crosses below zero (sellers take
control). Exits on the opposite zero-cross — once control flips back,
the thesis is gone. 2xATR hard stop, 2.5xATR chandelier trail,
150-bar max hold.

Source: Balance of Power (Igor Livshin, S&C Aug 2001) —
https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/balance-of-power-bop.md

## Limitations

- Single 7-month crypto window; 2,264 trades is a large sample, and
  all of it says the trigger loses — that is at least a confident
  negative result.
- Fees are the dominant line item (0.045% + 0.01% per side on 800+
  trades/coin); no strategy that trades this often survives them.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped length on this window (see CALIBRATION.md).
