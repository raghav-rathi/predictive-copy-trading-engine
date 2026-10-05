"""Slime Family agent-trading architecture, adapted to Hyperliquid perps.

"The AI proposes, the server decides."

Loop: stops first -> read market -> AI proposes (strict schema) ->
server validates every trade -> transaction previewed -> executed in
PAPER MODE ONLY -> everything posted to a public board.

Live execution is intentionally NOT wired: see README.md and the
paper-only disclaimer in runner.py.
"""

from .proposer import (
    Trade,
    Proposal,
    MarketSnapshot,
    Proposer,
    MomentumSlime,
    ScalperSlime,
    SnifferSlime,
    SurferSlime,
    DegenSlime,
    SPECIES,
)
from .risk_server import RiskServer, Verdict, RiskConfig
from .sellback import sellback_ok, SellbackConfig, BookFeed, StubBookFeed, HyperliquidBookFeed
from .watchdog import Watchdog, WatchdogConfig
from .preview import preview_trade, PreviewConfig
from .board import Board
from .runner import SlimeLoop, LoopConfig, PaperLedger

__all__ = [
    "Trade", "Proposal", "MarketSnapshot", "Proposer",
    "MomentumSlime", "ScalperSlime", "SnifferSlime", "SurferSlime",
    "DegenSlime", "SPECIES",
    "RiskServer", "Verdict", "RiskConfig",
    "sellback_ok", "SellbackConfig", "BookFeed", "StubBookFeed",
    "HyperliquidBookFeed",
    "Watchdog", "WatchdogConfig",
    "preview_trade", "PreviewConfig",
    "Board",
    "SlimeLoop", "LoopConfig", "PaperLedger",
]
