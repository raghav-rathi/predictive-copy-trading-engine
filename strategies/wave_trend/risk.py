"""WaveTrend Oscillator risk config.

WaveTrend is a fast mean-reversion oscillator: entries catch the
turn out of an oversold/overbought zone, so the 1.5xATR stop is
deliberately tight — a reversal that keeps running against you is
a failed reversal, and the whole premise dies if the oscillator
re-extends. The 2xATR chandelier trail locks in the turn when it
works. No fixed target: exits are oscillator-driven (opposite cross
or the ±60 extreme). 72-bar (~3-day) max hold keeps a stalled
reversal from tying up capital: on 1h bars a WaveTrend turn that
hasn't worked within three days is a thesis failure. Both directions
allowed — the oscillator is symmetric by construction.
"""

from strategies.base import RiskConfig

RISK = RiskConfig(
    atr_window=14,
    stop_atr_mult=1.5,
    trail_atr_mult=2.0,
    target_atr_mult=None,
    max_hold_bars=72,
    risk_frac=0.01,
    max_leverage=3.0,
    fee_rate=0.00045,
    slippage_rate=0.0001,
    allow_longs=True,
    allow_shorts=True,
)

WARMUP = 80  # EMA(21) chain + SMA(4) spin-up, with margin
