#!/usr/bin/env python3
"""Guardrail verification for the slime loop. All green required.

Proves, with deterministic stubs (no network):
  (a) an oversized / blocklisted proposal is refused by the risk server
  (b) a trade into a thin book is refused by the sell-back check
  (c) the watchdog fires a stop while the proposer is asleep
  (d) the board HTML renders with the trades and thoughts

Usage: python3 slime/verify_guardrails.py
Exit 0 = all green. PAPER MODE ONLY -- nothing here touches live.
"""
from __future__ import annotations

import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from slime.proposer import (MarketSnapshot, Proposal, Trade,
                            MomentumSlime, DegenSlime)
from slime.risk_server import RiskServer, RiskConfig
from slime.sellback import sellback_ok, SellbackConfig, StubBookFeed
from slime.watchdog import Watchdog, WatchdogConfig
from slime.board import Board
from slime.runner import SlimeLoop, LoopConfig, PaperLedger

PASS, FAIL = "PASS", "FAIL"
results: list[tuple[str, str, str]] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    results.append((PASS if cond else FAIL, name, detail))
    print(f"[{PASS if cond else FAIL}] {name}"
          + (f" -- {detail}" if detail else ""))


def deep_book(mid: float, depth_usd: float = 1_000_000) -> dict:
    """Book with plenty of depth on both sides."""
    qty = depth_usd / mid
    return {"mid": mid,
            "bids": [(mid * (1 - 0.0005 * i), qty / 10) for i in range(10)],
            "asks": [(mid * (1 + 0.0005 * i), qty / 10) for i in range(10)]}


def thin_book(mid: float) -> dict:
    """Only ~$120 of bids: a $1k exit cannot recover 80%."""
    return {"mid": mid,
            "bids": [(mid * 0.99, 120.0 / mid)],
            "asks": [(mid * 1.01, 120.0 / mid)]}


# ---------------------------------------------------------------- (a)
print("\n== (a) risk server refuses oversized / blocklisted ==")
cfg = RiskConfig(max_position_usd=500.0, max_open_positions=2)
server = RiskServer(cfg)
ledger = PaperLedger(10_000.0)
feed = StubBookFeed({"HYPE": deep_book(30.0)})

big = Trade("long", "HYPE", 50_000.0, "degen ape")
v = server.validate_trade(big, ledger, feed.get_book("HYPE"), "degen")
check("oversized refused", not v.ok and
      any("oversized" in r for r in v.reasons), f"{v.reasons}")

btc = Trade("long", "BTC", 100.0, "momentum btc")  # BTC is blocklisted
v = server.validate_trade(btc, ledger, feed.get_book("HYPE"), "momentum")
check("blocklisted coin refused", not v.ok and
      any("blocklist" in r for r in v.reasons), f"{v.reasons}")

ok_trade = Trade("long", "HYPE", 100.0, "momentum hype")
v = server.validate_trade(ok_trade, ledger, feed.get_book("HYPE"),
                          "momentum")
check("sane trade accepted", v.ok, f"{v.reasons}")

# max open positions
ledger.open("momentum", "HYPE", "long", 100.0, 30.0, time.time(), {})
ledger.open("momentum", "SOL", "long", 100.0, 200.0, time.time(), {})
v = server.validate_trade(ok_trade, PaperLedger(10_000.0), None, "m")
# fresh ledger with 0 positions is fine; now fill the real one
ledger2 = PaperLedger(10_000.0)
ledger2.open("a", "HYPE", "long", 100.0, 30.0, time.time(), {})
ledger2.open("a", "SOL", "long", 100.0, 200.0, time.time(), {})
v = server.validate_trade(ok_trade, ledger2, feed.get_book("HYPE"), "m")
check("max positions refused", not v.ok and
      any("max_open_positions" in r for r in v.reasons), f"{v.reasons}")
check("rejections logged", len(server.rejections) >= 3,
      f"{len(server.rejections)} rejections")

# ---------------------------------------------------------------- (b)
print("\n== (b) sell-back refuses thin book ==")
thin = thin_book(30.0)
ok, detail = sellback_ok("HYPE", "long", 1_000.0, thin)
check("thin book refused", not ok, detail["reason"])
check("recovery < 80%", detail["recovery_pct"] < 80.0 or not ok,
      f"recovery={detail.get('recovery_pct')}%")

deep = deep_book(30.0)
ok, detail = sellback_ok("HYPE", "long", 1_000.0, deep)
check("deep book accepted", ok, f"recovery={detail['recovery_pct']}%")

# ---------------------------------------------------------------- (c)
print("\n== (c) watchdog fires while proposer sleeps ==")
tmp = tempfile.mkdtemp(prefix="slime_verify_")
board = Board(os.path.join(tmp, "board.ndjson"))

books = {"HYPE": deep_book(30.0)}
feed = StubBookFeed(books)
snap_id = "s1"


def market_fn():
    return MarketSnapshot(snapshot_id=snap_id, ts=time.time(),
                          mids={"HYPE": 30.0},
                          chg_1h={"HYPE": 5.0}, chg_24h={"HYPE": 8.0},
                          funding={"HYPE": 0.0001},
                          volume_24h={"HYPE": 50_000_000},
                          whale_flow={"HYPE": 500_000.0})


loop_cfg = LoopConfig(
    board_path=os.path.join(tmp, "board.ndjson"),
    watchdog=WatchdogConfig(stop_loss_pct=2.0, take_profit_pct=6.0,
                            trailing_stop_pct=1.0),
)
loop = SlimeLoop(loop_cfg, feed, market_fn,
                 slime_names=["momentum"])  # degen excluded: would spam
s1 = loop.step()
check("momentum opened a paper position", s1["accepted"] >= 1,
      f"accepted={s1['accepted']}")

# Proposer goes to sleep: market frozen -> quiet turns only.
# Price crashes 5% through the 2% stop while it sleeps.
calls = {"n": 0}


def sleeping_market():
    calls["n"] += 1
    return MarketSnapshot(snapshot_id="s1", ts=time.time() + calls["n"],
                          mids={"HYPE": 28.5},   # -5% from 30.0
                          chg_1h={"HYPE": 0.0}, chg_24h={"HYPE": 0.0},
                          funding={}, volume_24h={}, whale_flow={})


loop.market_fn = sleeping_market
s2 = loop.step()
stops = [e for e in loop.board.read() if e.get("type") == "stop"]
check("watchdog fired stop while proposer asleep",
      any(e.get("reason") == "stop_loss" for e in stops),
      f"stops={[(e.get('coin'), e.get('reason')) for e in stops]}")
check("position closed by stop", len(loop.ledger.positions) == 0,
      f"open={len(loop.ledger.positions)}")
check("stop realized a loss (no fantasy fills)",
      loop.ledger.realized < 0, f"realized={loop.ledger.realized:+.2f}")

# ---------------------------------------------------------------- (d)
print("\n== (d) board HTML renders ==")
html_path = os.path.join(tmp, "board.html")
loop.board.render_html(html_path)
with open(html_path) as f:
    page = f.read()
check("html has trades table", "<table>" in page and "HYPE" in page)
check("html has thoughts feed",
      "momentum" in page and ("thought" in page.lower() or "Thoughts" in page))
check("html carries paper-mode banner", "PAPER MODE" in page)
check("html shows stop event", "stop_loss" in page or "STOP FIRED" in page)

print("\n== summary ==")
failed = [r for r in results if r[0] == FAIL]
print(f"{len(results) - len(failed)}/{len(results)} checks green")
sys.exit(1 if failed else 0)
