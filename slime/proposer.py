#!/usr/bin/env python3
"""Proposers: the AI side of "the AI proposes, the server decides".

A proposer NEVER executes. It reads a MarketSnapshot and returns a
strict Proposal: one thought (string) + a list of Trades. The
risk server (risk_server.py) decides what survives.

Built-in species are heuristic so the loop runs with NO API keys. An
LLM proposer can implement the same `Proposer` protocol and return the
same strict schema.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

@dataclass
class Trade:
    """One proposed trade. Size is USD notional; converted to coin units
    at execution from the mid price."""
    side: str          # "long" or "short"
    coin: str          # e.g. "HYPE"
    size_usd: float    # proposed notional in USD
    rationale: str     # one-line why

    def validate(self) -> list[str]:
        problems = []
        if self.side not in ("long", "short"):
            problems.append(f"side must be long|short, got {self.side!r}")
        if not self.coin or not isinstance(self.coin, str):
            problems.append("coin must be a non-empty string")
        if not isinstance(self.size_usd, (int, float)) \
                or self.size_usd <= 0:
            problems.append("size_usd must be a positive number")
        if not self.rationale:
            problems.append("rationale must be non-empty")
        return problems


@dataclass
class Proposal:
    slime: str
    thought: str
    trades: list[Trade] = field(default_factory=list)
    snapshot_id: str = ""

    def validate(self) -> list[str]:
        problems = []
        if not self.thought:
            problems.append("thought must be non-empty")
        for i, t in enumerate(self.trades):
            for p in t.validate():
                problems.append(f"trade[{i}]: {p}")
        return problems


@dataclass
class MarketSnapshot:
    """Everything a proposer is allowed to see."""
    snapshot_id: str
    ts: float
    mids: dict[str, float] = field(default_factory=dict)
    chg_1h: dict[str, float] = field(default_factory=dict)    # pct
    chg_24h: dict[str, float] = field(default_factory=dict)   # pct
    funding: dict[str, float] = field(default_factory=dict)  # hourly rate
    volume_24h: dict[str, float] = field(default_factory=dict)
    whale_flow: dict[str, float] = field(default_factory=dict)  # net USD


class Proposer(Protocol):
    """Anything that turns a market snapshot into a strict proposal."""
    name: str

    def propose(self, market: MarketSnapshot) -> Proposal: ...


# ---------------------------------------------------------------------------
# Species: strategy personalities, heuristic so no API keys are needed
# ---------------------------------------------------------------------------

class _Base:
    name = "base"

    def _proposal(self, market: MarketSnapshot, thought: str,
                  trades: list[Trade]) -> Proposal:
        return Proposal(slime=self.name, thought=thought, trades=trades,
                        snapshot_id=market.snapshot_id)


class MomentumSlime(_Base):
    """Rides strong 24h moves in the direction of the move, but refuses
    to chase when funding is extreme against the trade."""
    name = "momentum"
    MIN_24H = 4.0          # pct move to qualify
    MAX_FUNDING = 0.0008   # hourly; skip longs into heavily positive funding

    def propose(self, market: MarketSnapshot) -> Proposal:
        trades: list[Trade] = []
        cands = []
        for coin, chg in market.chg_24h.items():
            if abs(chg) >= self.MIN_24H and market.mids.get(coin, 0) > 0:
                cands.append((abs(chg), coin, chg))
        cands.sort(reverse=True)
        notes = []
        for _, coin, chg in cands[:2]:
            fund = market.funding.get(coin, 0.0)
            if chg > 0:
                if fund > self.MAX_FUNDING:
                    notes.append(f"{coin} +{chg:.1f}%/24h but funding "
                                 f"{fund:.5f}/h too hot; no chase")
                    continue
                trades.append(Trade("long", coin, 150.0,
                                    f"24h momentum +{chg:.1f}%, funding ok"))
            else:
                if fund < -self.MAX_FUNDING:
                    notes.append(f"{coin} {chg:.1f}%/24h but funding "
                                 f"{fund:.5f}/h too hot; no chase")
                    continue
                trades.append(Trade("short", coin, 150.0,
                                    f"24h breakdown {chg:.1f}%, funding ok"))
        thought = (f"momentum scan: {len(cands)} coins moved >="
                   f"{self.MIN_24H}%/24h. " +
                   (" ".join(notes) if notes else "taking the cleanest."))
        return self._proposal(market, thought, trades)


class ScalperSlime(_Base):
    """Mean-reversion scalper: fades sharp 1h spikes with small size."""
    name = "scalper"
    MIN_1H = 2.5
    SIZE = 75.0

    def propose(self, market: MarketSnapshot) -> Proposal:
        trades: list[Trade] = []
        spikes = [(abs(c), coin, c) for coin, c in market.chg_1h.items()
                  if abs(c) >= self.MIN_1H and market.mids.get(coin, 0) > 0]
        spikes.sort(reverse=True)
        for _, coin, chg in spikes[:2]:
            side = "short" if chg > 0 else "long"
            trades.append(Trade(side, coin, self.SIZE,
                                f"fade 1h spike {chg:+.1f}%"))
        thought = (f"scalper scan: {len(spikes)} 1h spikes >= "
                   f"{self.MIN_1H}%. " +
                   ("fading the sharpest." if trades else "nothing to fade."))
        return self._proposal(market, thought, trades)


class SnifferSlime(_Base):
    """On-chain flow sniffer: follows net whale flow with the trend."""
    name = "sniffer"
    MIN_FLOW = 250_000.0  # USD net flow to qualify

    def propose(self, market: MarketSnapshot) -> Proposal:
        trades: list[Trade] = []
        flows = [(abs(f), coin, f) for coin, f in market.whale_flow.items()
                 if abs(f) >= self.MIN_FLOW and market.mids.get(coin, 0) > 0]
        flows.sort(reverse=True)
        for _, coin, flow in flows[:2]:
            side = "long" if flow > 0 else "short"
            # only with the 24h trend, never against it
            chg = market.chg_24h.get(coin, 0.0)
            if (side == "long") != (chg >= 0):
                continue
            trades.append(Trade(side, coin, 120.0,
                                f"whale flow {flow:+,.0f} USD with 24h trend"))
        thought = (f"sniffer scan: {len(flows)} coins with whale flow >= "
                   f"${self.MIN_FLOW:,.0f}. " +
                   ("following flow with trend." if trades
                    else "no flow aligned with trend."))
        return self._proposal(market, thought, trades)


class SurferSlime(_Base):
    """Trend surfer: small entries only in the direction of the 1h trend,
    requires 24h agreement."""
    name = "surfer"
    MIN_1H = 1.0
    SIZE = 100.0

    def propose(self, market: MarketSnapshot) -> Proposal:
        trades: list[Trade] = []
        for coin, c1 in market.chg_1h.items():
            c24 = market.chg_24h.get(coin, 0.0)
            if abs(c1) < self.MIN_1H or (c1 > 0) != (c24 > 0):
                continue
            if market.mids.get(coin, 0) <= 0:
                continue
            side = "long" if c1 > 0 else "short"
            trades.append(Trade(side, coin, self.SIZE,
                                f"1h {c1:+.1f}% agrees with 24h {c24:+.1f}%"))
        trades = trades[:2]
        thought = (f"surfer scan: {len(trades)} trend-aligned setups. " +
                   ("riding." if trades else "waves too choppy."))
        return self._proposal(market, thought, trades)


class DegenSlime(_Base):
    """Degen: apes the biggest 1h mover with oversized size. The risk
    server exists precisely to say no to this slime."""
    name = "degen"
    SIZE = 50_000.0  # deliberately absurd; risk server caps it

    def propose(self, market: MarketSnapshot) -> Proposal:
        movers = sorted(
            ((abs(c), coin, c) for coin, c in market.chg_1h.items()
             if market.mids.get(coin, 0) > 0),
            reverse=True)
        trades: list[Trade] = []
        if movers:
            _, coin, chg = movers[0]
            side = "long" if chg > 0 else "short"
            trades.append(Trade(side, coin, self.SIZE,
                                f"APING biggest 1h mover {chg:+.1f}%"))
        thought = ("degen mode: biggest 1h mover gets the full send. "
                   "YOLO.")
        return self._proposal(market, thought, trades)


SPECIES: dict[str, type] = {
    "momentum": MomentumSlime,
    "scalper": ScalperSlime,
    "sniffer": SnifferSlime,
    "surfer": SurferSlime,
    "degen": DegenSlime,
}
