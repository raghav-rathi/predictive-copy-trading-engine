# Markov Regime Switching

James D. Hamilton's Markov regime-switching model (*A New
Approach to the Economic Analysis of Nonstationary Time Series*,
Econometrica, 1989): the return distribution switches between
unobserved states according to a Markov chain, and the state is
inferred probabilistically from the data. Here the two states are
a calm (low-volatility) regime and a turbulent (high-volatility)
regime on 1h log returns, and the regime selects which trading
system runs.

## Rules

- **Model:** 2-state Gaussian HMM on 1h log returns, fit from
  scratch with numpy (scaled forward-backward EM, 25 iterations,
  no external HMM library). States are labelled by fitted sigma:
  the larger-sigma state is turbulent.
- **Calibration:** fit once per coin on the first 1000 log returns
  of the window; thereafter the causal forward filter classifies
  each bar (turbulent when filtered P(turbulent) > 0.5).
- **Calm state (regime 0):** EMA(12)/EMA(26) cross trend system.
  Long on a cross up, short on a cross down.
- **Turbulent state (regime 1):** RSI(14) mean reversion. Long on
  a cross up through 30, short on a cross down through 70, exit
  at 50.
- **Exits:** either system's exit closes a position, whatever the
  current regime — long exits on an EMA cross down or an RSI cross
  down through 50; short exits on an EMA cross up or an RSI cross
  up through 50.
- The harness risk layer's 2xATR stop / 2.5xATR trail also applies;
  max hold 120 bars.
- Parameters are Hamilton's 2-state structure with the spec's
  system choices; nothing was tuned to this window.

All computation is causal given the fitted parameters, so signals
on bar i use only data through bar i's close (plus parameters fit
on the first 1000 bars — the documented calibration window).

## Source

- James D. Hamilton, "A New Approach to the Economic Analysis of
  Nonstationary Time Series", *Econometrica* 57(2), 1989:
  https://doi.org/10.2307/1912559

Paper only, no live execution.
