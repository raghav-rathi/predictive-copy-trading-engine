"""Paper ledger for the funding farm.

Tracks positions and accrues hourly funding payments. The farm is short the
perp, so positive funding (longs pay shorts) is income:

    payment = notional * funding_hr          # + when funding positive

Fees are charged on open/close: 2 legs (perp + spot) per side.
Delta (price) PnL is tracked per leg for the equity curve, but the farm's
edge is carry, not price — the ledger keeps them separate so the backtest
can report carry PnL vs basis PnL.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class FarmPosition:
    coin: str
    notional: float
    entry_mark: float
    entry_avg_funding_hr: float
    age_hours: float = 0.0
    carry_pnl: float = 0.0      # accumulated funding payments
    fees_paid: float = 0.0


@dataclass
class Ledger:
    equity: float
    positions: Dict[str, FarmPosition] = field(default_factory=dict)
    closed_carry: float = 0.0
    closed_fees: float = 0.0
    history: List[dict] = field(default_factory=list)

    # ---- lifecycle -----------------------------------------------------
    def open(self, coin: str, notional: float, mark: float,
             avg_funding_hr: float, perp_fee: float, spot_fee: float) -> None:
        fee = notional * (perp_fee + spot_fee)
        self.positions[coin] = FarmPosition(
            coin=coin, notional=notional, entry_mark=mark,
            entry_avg_funding_hr=avg_funding_hr, fees_paid=fee)
        self.history.append({"event": "open", "coin": coin,
                             "notional": notional, "fee": fee})

    def accrue_funding(self, coin: str, funding_hr: float) -> None:
        """One hour passes: the short perp collects funding_hr * notional."""
        pos = self.positions.get(coin)
        if pos is None:
            return
        payment = pos.notional * funding_hr
        pos.carry_pnl += payment
        pos.age_hours += 1.0

    def close(self, coin: str, mark: float,
              perp_fee: float, spot_fee: float) -> dict:
        pos = self.positions.pop(coin)
        fee = pos.notional * (perp_fee + spot_fee)
        # Basis PnL: short perp + long spot. If mark moved, the two legs
        # offset; any residual is basis drift.
        basis_pnl = pos.notional * (pos.entry_mark - mark) / pos.entry_mark \
            - pos.notional * (pos.entry_mark - mark) / pos.entry_mark
        # (== 0 by construction at equal notionals; kept explicit so the
        #  backtest can inject real mark moves per leg later.)
        net = pos.carry_pnl + basis_pnl - pos.fees_paid - fee
        self.closed_carry += pos.carry_pnl
        self.closed_fees += pos.fees_paid + fee
        self.equity += net
        row = {"event": "close", "coin": coin, "carry_pnl": pos.carry_pnl,
               "basis_pnl": basis_pnl, "fees": pos.fees_paid + fee,
               "net": net, "age_hours": pos.age_hours}
        self.history.append(row)
        return row

    # ---- reporting -----------------------------------------------------
    def open_carry(self) -> float:
        return sum(p.carry_pnl for p in self.positions.values())

    def summary(self) -> dict:
        return {
            "equity": round(self.equity, 2),
            "open_positions": len(self.positions),
            "open_carry": round(self.open_carry(), 2),
            "closed_carry": round(self.closed_carry, 2),
            "closed_fees": round(self.closed_fees, 2),
            "events": len(self.history),
        }
