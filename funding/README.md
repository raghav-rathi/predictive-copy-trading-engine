# Funding Farm

Delta-neutral funding harvester: **short perp + long spot** on the coins
with the highest trailing 7-day average funding rate. Harvests positive
funding while staying price-neutral — a second, uncorrelated book next to
the directional copy engine.

Paper-only. Not wired into the live copy engine.

## How it works

1. **Scan** (hourly): current funding for every perp (`metaAndAssetCtxs`).
2. **Rank**: trailing 168h mean funding from `fundingHistory`. Coins with
   <72h of history are not rankable.
3. **Enter**: top 1–2 coins clearing 0.0008%/hr (~7% APR), carry-weighted
   sizing capped at 25% of farm capital per coin, 1x legs.
4. **Switch**: move capital only when
   `(candidate_avg − held_avg) × 168h > 4-leg round-trip cost`
   (the djienne rule — churn only when carry gain pays the switch).
5. **Exit**: held coin's 7d avg turns negative (regime flip), or 30d max hold.

## Guardrails

- Negative 7d realized carry → pause new entries.
- 5% equity drawdown from peak → pause.
- Per-coin concentration cap re-checked every step.

## Layout

| file | purpose |
|---|---|
| `FUNDING_FARM_DESIGN.md` | thesis, mechanics, risks, kill criteria |
| `BACKTEST_RESULTS.md` | 30d historical backtest outcome |
| `config.py` | `FarmConfig` defaults |
| `api.py` | funding data access (current + history) |
| `ranking.py` | trailing-average ranking, thin-history guard |
| `strategy.py` | enter/switch/exit decision rules |
| `sizing.py` | carry-weighted sizing, per-coin cap |
| `ledger.py` | paper ledger, hourly funding accrual, carry vs basis |
| `paper.py` | hourly paper runner (scan → rank → decide → ledger) |
| `guardrails.py` | pause conditions |
| `tests/` | 17 unit tests |

## Running the backtest

```bash
python3 scripts/backtest_funding.py --days 30 --top 20
```

## Status

- [x] Design doc
- [x] Core logic + paper runner
- [x] 17/17 unit tests green
- [ ] 30d historical backtest (running)
- [ ] 30d live paper run
- [ ] Capital-split decision vs copy book (after paper numbers)
