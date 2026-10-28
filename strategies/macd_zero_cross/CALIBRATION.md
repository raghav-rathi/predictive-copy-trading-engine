# MACD Zero Cross — Calibration

## Parameter choices

MACD(12,26,9) is Appel's canonical setting, used unchanged — no fitting to this window. Warmup 40 bars covers EMA(26) plus the signal EMA with margin. The 2xATR stop / 2.5xATR trail / 168-bar max hold is the batch risk standard, shared across all four strategies so their results are comparable.

## Sensitivity note

No parameter sweep was run on this window; the shipped MACD(12,26,9) is Appel's textbook setting, chosen a priori. Shortening the EMAs would add crosses (and whipsaws) in chop; lengthening them would delay entries further into established moves. Either direction trades one failure mode for the other, and tuning on this single window would be overfitting — the honest conclusion is that the rule itself, not its parameters, is the problem here.

## Verdict

LOSER. Combined −$1,222 across 572 trades (−$2.14 expectancy). The least-bad strategy in this batch — HYPE is mildly green and the drawdowns are the shallowest here — but BTC (−$1,745, Sharpe −1.38) and ETH (−$237) both lose, and a 31–37% win rate with profit factors under 1.09 on every leg is not a tradable edge. The zero cross is a trend filter, not a timing signal, and on 1h crypto it pays for that lateness in chop.
