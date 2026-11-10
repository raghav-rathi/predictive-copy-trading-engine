# Bill Williams Market Facilitation Index Squat Breakout

Bill Williams' Market Facilitation Index (MFI) from *Trading Chaos*:
MFI = (high − low) / volume. Only the bar-to-bar change matters, so
each bar is classified against the previous one — GREEN (MFI up,
volume up), FADE (MFI down, volume down), FAKE (MFI up, volume down),
SQUAT (MFI down, volume up). A SQUAT bar is heavy volume on little
range: buyers and sellers battling, which Williams reads as often
preceding a breakout.

## Rules

- Remember the most recent SQUAT bar (its high/low); a newer squat replaces it.
- Long: a bar closes above the squat bar's high within the next 5 bars (squat bar excluded), AND the close is above EMA(20).
- Short: a bar closes below the squat bar's low within the next 5 bars, AND the close is below EMA(20).
- Exit a long on a FADE bar (interest fading) or a close below EMA(20); exit a short on a FADE bar or a close above EMA(20).
- ATR stop / trail from the risk layer also applies.
- All computation is causal, so signals on bar i use only data through bar i's close. Not to be confused with the Money Flow Index (a different indicator that shares the MFI acronym).

## Source

- Bill Williams, *Trading Chaos* (Wiley, 1995) — BW MFI and the four bar types
- LuxAlgo concept reference: https://www.luxalgo.com/library/concept/bill-williams-market-facilitation-index/

Paper only, no live execution.
