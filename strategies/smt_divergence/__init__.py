"""SMT divergence (ICT Smart Money Technique): registration + re-exports.

Note: ``add_indicators`` expects a merged BTC/ETH frame from
``indicators.build_merged_frame(traded_df, ref_df)``, not a
single-coin frame (same pattern as pairs_spread's spread frame).
"""

from strategies.smt_divergence import indicators, risk, signals
from strategies.base import StrategySpec
from strategies.registry import register

SPEC = register(
    StrategySpec(
        name="SMT Divergence",
        slug="smt_divergence",
        description="ICT Smart Money Technique divergence on causal 5-bar pivots: bullish SMT is the traded coin printing a lower swing low while the reference coin prints a higher swing low (lows within 10 bars) — long on the first close above the traded coin's prior swing high within 20 bars; bearish is the mirror; exit on the opposite SMT signal or a close through the divergence swing extreme, plus the harness stop/trail. Backtested as two $10k books (BTC traded / ETH ref, and ETH traded / BTC ref); HYPE excluded (no pair).",
        source_name="ICT SMT Divergence (The Inner Circle Traders)",
        source_url="https://www.theinnercircletraders.com/ict-smt-divergence/",
        warmup_bars=risk.WARMUP,
        add_indicators=indicators.add_indicators,
        add_signals=signals.add_signals,
        risk=risk.RISK,
    )
)

__all__ = ["indicators", "signals", "risk", "SPEC"]
