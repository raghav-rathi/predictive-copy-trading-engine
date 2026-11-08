# ADX / DI Crossover

Wilder DMI(14) crossover with an ADX trend filter. +DM/-DM and true range are Wilder-smoothed (alpha 1/14); +DI = 100 × smoothed(+DM)/ATR, −DI = 100 × smoothed(−DM)/ATR, DX = 100 × |+DI − −DI|/(+DI + −DI), ADX = Wilder-smoothed DX (alpha 1/14).

## Rules

- Long: +DI crosses above −DI AND ADX > 25 AND ADX rising (above its previous bar) AND (+DI − −DI) ≥ 5 at the cross. Exit on −DI crossing above +DI or ADX < 20.
- Short: mirror — −DI crosses above +DI with ADX > 25, rising, and (−DI − +DI) ≥ 5. Exit on +DI crossing above −DI or ADX < 20.
- All smoothing is causal, so signals on bar i use only data through bar i's close. ATR stop / trail from the risk layer also applies.

## Source

- JournalPlus — ADX Trading Strategy: https://journalplus.co/strategies/adx-trading-strategy/

Paper only, no live execution.
