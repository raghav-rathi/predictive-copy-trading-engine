"""BOT 4 - GATE.

The ONLY bot allowed to emit trade alerts. Alerts only - it NEVER places
orders. There is intentionally no order-placement code path anywhere in this
module (or package); live execution raises NotImplementedError by design
(see executor.py).

Skip rules (skipped alerts are journaled by the Auditor, never dropped):
  NO_FRESH_ZONE       ladder has no untested zone -> no alert emitted
  TESTED_ZONE         best (highest) zone already TESTED -> alert flagged SKIP
  INVALID_SIZE        the Risk Officer rejects the sizing
  ZONE_INVALIDATED    a 1H close above the zone top killed the zone
  EXPIRED             alert older than ALERT_MAX_LIFE_DAYS without a 1H touch
  POSITION_ALREADY_OPEN  position open on the coin and not at breakeven
"""
import datetime
from dataclasses import dataclass, field

from .config import get


@dataclass
class Alert:
    alert_id: str
    coin: str
    asof_ms: int
    zone_top: float
    zone_bottom: float
    stop: float            # = zone top per charter
    prime: bool
    anchor_high: float
    ladder_snapshot: list = field(default_factory=list)  # [(top, bottom, state)]
    # filled by the backtest once sized:
    entry: float = 0.0
    qty: float = 0.0
    notional: float = 0.0
    risk_pct: float = 0.0
    risk_amount: float = 0.0
    skip_reason: str = ""  # "" = clean alert; else one of the SKIP codes

    @property
    def skipped(self):
        return bool(self.skip_reason)


def _alert_id(coin, asof_ms):
    return f"{coin}-{asof_ms}"


def evaluate(coin, ladder, asof_ms, position=None):
    """Build the gate decision for a fresh flip.

    Returns (Alert|None, skip_code). A TESTED best zone still produces an
    Alert object flagged SKIP so the Auditor can journal (and shadow-price)
    it; NO_FRESH_ZONE / INVALID_SIZE return (None, code).
    """
    if ladder is None or not ladder.zones:
        return None, "NO_FRESH_ZONE"
    best = ladder.best()
    if best is None:
        return None, "NO_FRESH_ZONE"

    if position is not None and not position.at_breakeven():
        return None, "POSITION_ALREADY_OPEN"

    skip = ""
    if best.state == "TESTED":
        skip = "TESTED_ZONE"

    alert = Alert(
        alert_id=_alert_id(coin, asof_ms), coin=coin, asof_ms=asof_ms,
        zone_top=best.top, zone_bottom=best.bottom, stop=best.top,
        prime=False,  # set by caller from the FlipEvent
        anchor_high=ladder.anchor_high,
        ladder_snapshot=[(z.top, z.bottom, z.state) for z in ladder.zones],
        risk_pct=get("RISK_PCT_INITIAL"),
        skip_reason=skip,
    )
    return alert, skip


def expired(alert, now_ms):
    return (now_ms - alert.asof_ms) > get("ALERT_MAX_LIFE_DAYS") * 86400 * 1000


def format_telegram(alert):
    """Render the Telegram-style alert message."""
    dt = datetime.datetime.fromtimestamp(
        alert.asof_ms / 1000, tz=datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    prime = "PRIME " if alert.prime else ""
    skip = f"\nSKIP: {alert.skip_reason}" if alert.skipped else ""
    return (
        f"\n[GATE] {prime}SHORT {alert.coin} | {dt}{skip}\n"
        f"Zone: {alert.zone_bottom:.6g} - {alert.zone_top:.6g} (4H FVG)\n"
        f"Entry: {alert.entry:.6g} | Stop: {alert.stop:.6g} (zone top)\n"
        f"Size: {alert.qty:.6g} ({alert.notional:,.2f} USD notional)\n"
        f"Risk: {alert.risk_pct}% ({alert.risk_amount:,.2f} USD) | "
        f"Anchor high: {alert.anchor_high:.6g}"
    )
