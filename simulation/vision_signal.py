"""Vision-stack ($SGHV) signal processing — envelope amplitude, phase
coherence, and an eta_tink coupling-efficiency estimate.

Round 1 (PR #1) wired `$SGHV` framing/checksum/multiplexing all the way
through `daq/protocol.py` and `daq/serial_sensors.py`, but nothing
downstream interpreted `us_amplitude_mV` / `us_phase_deg` /
`piezo_array_V` samples as a signal. This module is that missing layer:
real, if intentionally lightweight, signal processing feeding the
UDT/AOR/VOH math already in `simulation/differential_tink.py`.

Two real algorithms, each independently testable against synthetic
sine-wave streams with known ground truth:

  * Windowed RMS/envelope amplitude estimation over a rolling buffer of
    `us_amplitude_mV` samples.
  * Circular-statistics phase coherence: the resultant vector length
    R = |mean(exp(i * phase))| of `us_phase_deg` samples (converted to
    radians), which is the standard measure of how tightly clustered a
    set of angles is (R=1 -> perfectly phase-locked, R->0 -> uniformly
    random phase). This generalizes the single-sample
    `abs(mean(cos(phase)))` shortcut used in
    `differential_tink.tink_kernel` (which assumes phase is already
    referenced to zero) to real multi-sample phase-coherence estimation
    where the reference phase is not known in advance.

Spec: docs/UDT_PHYSICS.md, docs/VOH_PHYSICS.md, docs/AOR_PHYSICS.md.
"""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass, field

import numpy as np

from simulation.constants import ETA_TINK_DEFAULT

DEFAULT_WINDOW = 32


@dataclass
class VisionSample:
    t_s: float
    us_amplitude_mV: float
    us_phase_deg: float
    piezo_array_V: float


@dataclass
class VisionSignalSummary:
    n_samples: int
    rms_amplitude_mV: float
    peak_amplitude_mV: float
    mean_piezo_V: float
    phase_coherence_R: float  # in [0, 1]; 1 = perfectly phase-locked
    eta_tink_estimate: float


def rms_amplitude(amplitudes_mV: np.ndarray) -> float:
    """Windowed RMS (root-mean-square) envelope amplitude estimate."""
    if amplitudes_mV.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(amplitudes_mV))))


def phase_coherence(phase_deg: np.ndarray) -> float:
    """Circular resultant length R = |mean(exp(i * phase))|, phase_deg in degrees.

    R = 1.0 means every sample has identical phase (perfectly coherent /
    phase-locked ultrasonic drive). R -> 0 means phases are uniformly
    scattered (incoherent). This is the standard circular-statistics
    measure of angular concentration (Mardia & Jupp, "Directional
    Statistics"), applied here to `$SGHV` us_phase_deg samples.
    """
    if phase_deg.size == 0:
        return 0.0
    phase_rad = np.deg2rad(phase_deg)
    resultant = np.mean(np.exp(1j * phase_rad))
    return float(np.abs(resultant))


def estimate_eta_tink(
    rms_amp_mV: float,
    coherence_R: float,
    *,
    amp_reference_mV: float = 250.0,
    eta_tink_max: float = ETA_TINK_DEFAULT,
) -> float:
    """Bridge measured vision-stack signal quality to an eta_tink estimate.

    eta_tink (simulation.constants.ETA_TINK_DEFAULT, the UDT
    Tink-coupling efficiency consumed by
    `differential_tink.tink_kernel`/`sweep_eta_tink`) is presently a
    literature placeholder. Given real amplitude + phase-coherence
    measurements, this scales eta_tink_max by (normalized amplitude) *
    (phase coherence), clamped to [0, eta_tink_max] -- i.e. a weak or
    incoherent ultrasonic drive is estimated to couple less efficiently
    than the literature ceiling, and a strong, phase-locked drive
    approaches it. This is a calibration *estimator*, not a replacement
    for a real T1b-fit eta_tink (docs/ROADMAP.md M2 / M7b).
    """
    amp_factor = min(max(rms_amp_mV / max(amp_reference_mV, 1e-9), 0.0), 1.0)
    coherence_factor = min(max(coherence_R, 0.0), 1.0)
    return eta_tink_max * amp_factor * coherence_factor


def summarize(samples: list[VisionSample], *, amp_reference_mV: float = 250.0) -> VisionSignalSummary:
    """Summarize a batch of vision-stack samples into the quantities the
    UDT/AOR/VOH math consumes."""
    if not samples:
        return VisionSignalSummary(0, 0.0, 0.0, 0.0, 0.0, 0.0)

    amps = np.array([s.us_amplitude_mV for s in samples], dtype=float)
    phases = np.array([s.us_phase_deg for s in samples], dtype=float)
    piezo = np.array([s.piezo_array_V for s in samples], dtype=float)

    rms = rms_amplitude(amps)
    coherence = phase_coherence(phases)
    eta_est = estimate_eta_tink(rms, coherence, amp_reference_mV=amp_reference_mV)

    return VisionSignalSummary(
        n_samples=len(samples),
        rms_amplitude_mV=rms,
        peak_amplitude_mV=float(np.max(np.abs(amps))),
        mean_piezo_V=float(np.mean(piezo)),
        phase_coherence_R=coherence,
        eta_tink_estimate=eta_est,
    )


@dataclass
class RollingVisionProcessor:
    """Maintains a fixed-size rolling window of vision-stack samples and
    recomputes the signal summary incrementally as new samples arrive
    (e.g. one per `$SGHV` frame decoded by daq/serial_sensors.py)."""

    window: int = DEFAULT_WINDOW
    amp_reference_mV: float = 250.0
    _buffer: deque = field(default_factory=lambda: deque(maxlen=DEFAULT_WINDOW))

    def __post_init__(self) -> None:
        # deque's maxlen was bound at dataclass-field-default-factory time
        # (DEFAULT_WINDOW); rebuild it if a custom window was requested.
        if self._buffer.maxlen != self.window:
            self._buffer = deque(maxlen=self.window)

    def add_sample(self, sample: VisionSample) -> None:
        self._buffer.append(sample)

    def add_row(self, row: dict) -> None:
        """Convenience: add a sample from a raw dict (e.g. a decoded
        $SGHV frame's `.values`, optionally with `t_s`/`t`/`frame_seq`)."""
        self.add_sample(
            VisionSample(
                t_s=float(row.get("t_s", row.get("t", 0.0))),
                us_amplitude_mV=float(row["us_amplitude_mV"]),
                us_phase_deg=float(row["us_phase_deg"]),
                piezo_array_V=float(row["piezo_array_V"]),
            )
        )

    def summary(self) -> VisionSignalSummary:
        return summarize(list(self._buffer), amp_reference_mV=self.amp_reference_mV)

    def __len__(self) -> int:
        return len(self._buffer)
