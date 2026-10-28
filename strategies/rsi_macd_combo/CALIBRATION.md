# RSI + MACD Confluence — Calibration

## Parameter choices

RSI(14) is Wilder's standard period and the 50 midline is the momentum-regime boundary (not the 30/70 oversold/overbought levels, which suit reversals, not trend entries). MACD(12,26,9) is Appel's canonical setting. The asymmetry — histogram required for entry, RSI alone for exit — is deliberate: exits should be fast, entries should be confirmed. Warmup 40 bars covers MACD(26) plus signal EMA with margin. Risk is the batch standard.

## Sensitivity note

No parameter sweep was run on this window; RSI(14) and MACD(12,26,9) are the textbook settings, chosen a priori. Requiring a stronger histogram (e.g. hist > some threshold) would delay entries further; dropping the histogram condition collapses the strategy into a bare RSI-50 system, which whipsaws worse. The failure is in the trigger/exit pairing, not a tunable constant.

## Verdict

LOSER. Combined −$5,940 across 1,039 trades (−$5.72 expectancy). The confluence idea is sound in principle — requiring two indicators to agree should cut false signals — but on this window it mostly delays entries into moves already underway while the RSI-recross exit churns positions: 19.4% win rate on ETH is the batch's lowest single-leg print. HYPE's green leg (+$1,056) is the only bright spot and is far too thin to outweigh two heavy losing legs.
