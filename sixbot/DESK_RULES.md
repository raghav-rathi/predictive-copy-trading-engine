# SIX-BOT DESK — CHARTERS

> Single source of truth for the `sixbot/` package.
> Transcribed from @0xNevsky, "Grok Bot for Traders: The 6-Bot Desk I Actually
> Run (Full Setup + Charters)" (X article, Sep 25 2026).
>
> Every bot module reads its operating parameters from the LOCKED PARAMETERS
> block below (parsed by `sixbot/config.py`). The GO/NO-GO thresholds were
> fixed BEFORE the first backtest run and are never tuned after seeing results.
>
> Lines marked *(assumption)* fill a gap the article's public text left open;
> the choice is documented in `README.md` and was NOT tuned to the data.

## LOCKED PARAMETERS

```params
ACCOUNT_EQUITY_USD = 10000
RISK_PCT_INITIAL = 1.0        # (assumption) article's risk% not visible; 1% is the conventional default
RISK_PCT_ADD = 0.5            # per charter: each add = 0.5% risk
MAX_ADDS_PER_POSITION = 2     # (assumption) cap on adds per position
FEE_PCT_PER_SIDE = 0.05       # taker fee, charged per side
SLIPPAGE_PCT_PER_SIDE = 0.02  # (assumption) "small slippage"
ENTRY_TIMING = next_1h_open_after_confirmation
STOP_LEVEL = zone_top         # stop = zone top, no buffer
ANCHOR_LOOKBACK_DAYS = 30     # (assumption) impulse anchor search window
ALERT_MAX_LIFE_DAYS = 14      # (assumption) alert expires if the zone is never touched
STALE_HOURS = 72              # flat for 72h -> STALE flag
STALE_MIN_MOVE_R = 0.5        # (assumption) "flat" = max favorable excursion < 0.5R
PRIME_4H_BOUNCE_BARS = 6      # (assumption) bounce lookback for the PRIME tag
FVG_MIN_DISPLACEMENT_ATR_MULT = 0.5  # (assumption) impulse-candle quality filter
FVG_ATR_PERIOD = 14
GO_NOGO_TRADES_MIN = 40
GO_NOGO_WIN_RATE_MIN = 0.33
GO_NOGO_EXPECTANCY_MIN_R = 0.4
GO_NOGO_MAX_DD_MAX = 0.20
```

---

## BOT 1 — SCREENER

**Role.** Watches daily closes and emits flip events. It does not trade.

**Rules.**

1. The desk is SHORT-ONLY. Only bearish flips are tradeable.
2. Bearish flip — three consecutive closed daily candles C1, C2, C3:
   - C1 closes down: `C1.close < C1.open`.
   - C2 closes below C1's close (`C2.close < C1.close`) and does NOT take out
     C1's high (`C2.high < C1.high` — strict: it may not even touch it).
   - C3's body closes below C2's close (`C3.close < C2.close`) and C3 does not
     touch C1's high (`C3.high < C1.high`).
   - Dojis are valid candles. C2 does NOT need to be red.
3. PRIME tag — if the daily flipped down while the 4H is bouncing, tag the
   flip PRIME. This is the preferred entry. Bouncing = the latest closed 4H
   candle is green and price is above the lowest low of the last
   `PRIME_4H_BOUNCE_BARS` 4H candles *(assumption: exact bounce test)*.
4. Bullish flips (the mirror image) are logged as context only. They are
   NEVER traded.

**Output.** `FlipEvent(coin, date, direction, prime)`.

---

## BOT 2 — CARTOGRAPHER

**Role.** For each watchlist coin, maps where a short can enter. It does not
trade and does not size.

**Rules.**

1. Anchor the impulse: `anchor_high` = highest daily high of the last
   `ANCHOR_LOOKBACK_DAYS` days ending at C1; `current_low` = lowest daily low
   from the anchor to now.
2. Scan 4H candles across the FULL impulse (anchor high → current low) for
   bearish Fair Value Gaps: any 3-candle window where
   `candle[i-2].low > candle[i].high` (the red middle candle displaced down
   so hard it left a gap above), with the middle candle a red
   displacement candle whose range exceeds
   `FVG_MIN_DISPLACEMENT_ATR_MULT × ATR(FVG_ATR_PERIOD)`
   *(assumption: quality filter; the article just says "Fair Value Gaps")*.
   The zone is `[candle[i].high, candle[i-2].low]`; top = `candle[i-2].low`,
   bottom = `candle[i].high`.
3. Build the ladder top-to-bottom (highest zone first). Merge overlapping zones.
4. Zone state:
   - FRESH until price wicks into it.
   - A partial wick test — a 4H high enters the zone while the 4H close stays
     below the zone top — marks the zone TESTED.
   - A 4H close above the zone top INVALIDATES the zone (removed from ladder).
5. Confirmation happens on the 1H: a 1H candle wicks into the zone
   (`high >= zone_bottom`) and closes back below the zone top → rejection
   confirmed, entry permitted at the next 1H open.

**Output.** `Ladder(coin, asof, anchor_high, zones[...])` sorted top-to-bottom.

---

## BOT 3 — RISK OFFICER

**Role.** Position sizing. It NEVER looks at charts — only numbers.

**Rules.**

1. Inputs: account equity, entry price, stop price, risk%.
2. `risk_amount = equity × risk_pct / 100`
   `qty = risk_amount / (stop − entry)` (short: stop > entry)
   `notional = qty × entry`
   Reject (INVALID_SIZE) if `stop ≤ entry`.
3. Initial entries use `RISK_PCT_INITIAL`. Every add uses `RISK_PCT_ADD`.
4. An add is approved ONLY if the previous entry on that coin is at breakeven
   (its stop has been moved to its entry price). At most
   `MAX_ADDS_PER_POSITION` adds per position.

---

## BOT 4 — GATE

**Role.** The ONLY bot allowed to emit trade alerts. Alerts only — it NEVER
places orders. (This repo has no live trading by design; `executor.py`
raises `NotImplementedError` if called.)

**Rules.**

1. Alert object: coin, zone top/bottom, entry, stop, size (qty + notional),
   risk%, PRIME tag, chart data (anchor high, flip date, ladder snapshot).
2. Renders a Telegram-style alert message for each alert.
3. Skip rules — skipped alerts are journaled by the Auditor, never silently
   dropped:
   - `NO_FRESH_ZONE` — the ladder has no untested zone; no alert is emitted.
   - `TESTED_ZONE` — the best (highest) zone is already TESTED; the alert is
     flagged SKIP (edge consumed).
   - `INVALID_SIZE` — the Risk Officer rejects the sizing.
   - `ZONE_INVALIDATED` — a 1H close above the zone top killed the zone.
   - `EXPIRED` — the alert lived longer than `ALERT_MAX_LIFE_DAYS` without a
     1H touch.
   - `POSITION_ALREADY_OPEN` — a position is already open on the coin and it
     is not at breakeven (so no add is allowed either).
4. PRIME is the preferred entry, but non-PRIME alerts are still emitted.

---

## BOT 5 — EXIT CLERK

**Role.** Manages open positions on 4H and daily closes. No discretion.

**Rules.**

1. On 4H closes: if price trades at/through the stop (`STOP_LEVEL` = zone
   top), EXIT at the stop. Evaluated intrabar on 4H highs; the fill is assumed
   at the stop price.
2. On daily closes: a daily close above the anchor (anchor high) → EXIT
   immediately at the close. Catastrophic-invalidation backstop.
3. While in profit and no exit signal fires: state NEUTRAL → hold. No
   discretionary exits, no trailing, no take-profit in this charter.
4. Flat for `STALE_HOURS` with max favorable excursion below
   `STALE_MIN_MOVE_R` → flag STALE and exit at market *(assumption: the
   article says "flag"; the paper desk exits so dead capital is journaled)*.
5. Breakeven management: once price moves 1R in favor (one full stop-distance),
   move the stop to the entry price. This is what unlocks adds under the Risk
   Officer.

---

## BOT 6 — AUDITOR

**Role.** Journals everything and grades the desk against the locked
thresholds.

**Rules.**

1. Journal EVERY trade: entry, exit, fee, slippage — each on its own line —
   and the result in R (net PnL ÷ total risked).
2. Journal every SKIPPED alert with its reason.
3. Grade against the go/no-go thresholds (locked BEFORE the backtest, never
   tuned after):
   - trades ≥ `GO_NOGO_TRADES_MIN`
   - win rate ≥ `GO_NOGO_WIN_RATE_MIN`
   - expectancy ≥ `GO_NOGO_EXPECTANCY_MIN_R` (mean R)
   - max drawdown ≤ `GO_NOGO_MAX_DD_MAX` (fraction of equity, daily MTM)
4. Verdict per threshold: PASS / FAIL. If any threshold fails, the desk does
   not go live. No re-tuning after seeing the results.
