"""Tests for simulation/vision_signal.py using synthetic sine-wave streams.

No hardware needed: samples are generated in-memory with known
amplitude/phase so the RMS and circular-coherence math can be checked
against closed-form expected values.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from simulation.vision_signal import (
    RollingVisionProcessor,
    VisionSample,
    estimate_eta_tink,
    phase_coherence,
    rms_amplitude,
    summarize,
)


def test_rms_amplitude_of_constant_signal_equals_the_constant():
    amps = np.full(50, 250.0)
    assert rms_amplitude(amps) == pytest.approx(250.0)


def test_rms_amplitude_of_sine_wave_matches_closed_form():
    # RMS of A*sin(x) over many periods -> A / sqrt(2)
    A = 100.0
    x = np.linspace(0, 20 * math.pi, 4000)
    amps = A * np.sin(x)
    assert rms_amplitude(amps) == pytest.approx(A / math.sqrt(2), rel=1e-3)


def test_rms_amplitude_empty_is_zero():
    assert rms_amplitude(np.array([])) == 0.0


def test_phase_coherence_perfectly_locked_is_one():
    phases = np.full(40, 37.5)  # identical phase every sample
    assert phase_coherence(phases) == pytest.approx(1.0, abs=1e-9)


def test_phase_coherence_uniform_random_is_near_zero():
    rng = np.random.default_rng(42)
    phases = rng.uniform(0, 360, size=5000)
    R = phase_coherence(phases)
    assert R < 0.05  # should be close to 0 for a large uniform sample


def test_phase_coherence_partial_scatter_is_between():
    rng = np.random.default_rng(7)
    # tight cluster around 90 deg with small jitter -> high but not-quite-1 R
    phases = 90.0 + rng.normal(0, 5.0, size=1000)
    R = phase_coherence(phases)
    assert 0.9 < R < 1.0


def test_estimate_eta_tink_scales_with_amplitude_and_coherence():
    strong_coherent = estimate_eta_tink(rms_amp_mV=250.0, coherence_R=1.0, amp_reference_mV=250.0)
    weak_incoherent = estimate_eta_tink(rms_amp_mV=25.0, coherence_R=0.1, amp_reference_mV=250.0)
    assert strong_coherent > weak_incoherent
    assert strong_coherent == pytest.approx(0.15)  # ETA_TINK_DEFAULT * 1.0 * 1.0


def test_estimate_eta_tink_is_clamped_to_zero_and_max():
    over_amp = estimate_eta_tink(rms_amp_mV=10_000.0, coherence_R=5.0, amp_reference_mV=250.0)
    assert over_amp <= 0.15 + 1e-9
    negative_like = estimate_eta_tink(rms_amp_mV=0.0, coherence_R=0.0)
    assert negative_like == pytest.approx(0.0)


def test_summarize_empty_list_returns_zeroed_summary():
    summary = summarize([])
    assert summary.n_samples == 0
    assert summary.rms_amplitude_mV == 0.0
    assert summary.phase_coherence_R == 0.0


def test_summarize_coherent_strong_signal():
    samples = [
        VisionSample(t_s=float(i), us_amplitude_mV=250.0, us_phase_deg=12.0, piezo_array_V=1.2)
        for i in range(20)
    ]
    summary = summarize(samples)
    assert summary.n_samples == 20
    assert summary.rms_amplitude_mV == pytest.approx(250.0)
    assert summary.phase_coherence_R == pytest.approx(1.0, abs=1e-9)
    assert summary.mean_piezo_V == pytest.approx(1.2)
    assert summary.eta_tink_estimate == pytest.approx(0.15)


def test_rolling_processor_evicts_oldest_beyond_window():
    proc = RollingVisionProcessor(window=3)
    for i in range(5):
        proc.add_sample(VisionSample(t_s=float(i), us_amplitude_mV=float(i * 10), us_phase_deg=0.0, piezo_array_V=1.0))
    assert len(proc) == 3
    summary = proc.summary()
    # only the last 3 samples (amps 20,30,40) should be in the window
    assert summary.rms_amplitude_mV == pytest.approx(math.sqrt((20**2 + 30**2 + 40**2) / 3))


def test_rolling_processor_add_row_from_frame_values():
    proc = RollingVisionProcessor(window=5)
    proc.add_row({"t_s": 1.0, "us_amplitude_mV": 200.0, "us_phase_deg": 5.0, "piezo_array_V": 1.1})
    proc.add_row({"us_amplitude_mV": 220.0, "us_phase_deg": 5.0, "piezo_array_V": 1.1})
    assert len(proc) == 2
    summary = proc.summary()
    assert summary.n_samples == 2
