"""Tests for daq/serial_sensors.py fallback and framing behavior.

No real hardware is used. A fake serial.Serial-like object feeds
synthetic byte streams (built with daq.protocol.encode_frame) through
SerialLink to prove the real ingestion path, checksum rejection, and
the explicit (never-silent) fallback-to-simulation behavior.
"""

from __future__ import annotations

import warnings

import pytest

from daq.protocol import encode_frame
from daq.serial_sensors import FallbackToSimulation, SerialLink, read_sensors_serial

SAMPLE_VALUES = {
    "p_feed_bar": 0.5,
    "p_draw_bar": 34.0,
    "q_feed_L_min": 2.0,
    "q_draw_L_min": 0.15,
    "cond_feed_mS_cm": 8.0,
    "cond_draw_mS_cm": 85.0,
    "t_feed_C": 22.0,
    "t_draw_C": 23.0,
    "p_elec_W": 1.66,
}


class FakeSerial:
    """Minimal stand-in for serial.Serial reading from a preloaded byte buffer."""

    def __init__(self, chunks: list[bytes]):
        self._chunks = list(chunks)

    def readline(self) -> bytes:
        if self._chunks:
            return self._chunks.pop(0)
        return b""  # simulate a read timeout with no data

    def close(self) -> None:
        pass


def _make_link_with_chunks(chunks: list[bytes]) -> SerialLink:
    link = SerialLink(port="/dev/fake", read_timeout=0.2)
    link._conn = FakeSerial(chunks)
    return link


def test_read_frame_returns_valid_frame_from_hardware_bytes():
    frame_bytes = encode_frame(seq=1, millis=1000, values=SAMPLE_VALUES)
    link = _make_link_with_chunks([frame_bytes])
    frame = link.read_frame(deadline_s=0.5)
    assert frame is not None
    assert frame.seq == 1
    assert link.frames_ok == 1
    assert link.frames_bad == 0


def test_read_frame_drops_bad_checksum_and_counts_it():
    frame_bytes = encode_frame(seq=2, millis=2000, values=SAMPLE_VALUES)
    corrupted = frame_bytes.replace(b"*", b"@", 1) if b"*" in frame_bytes else frame_bytes
    # ensure it's actually malformed (missing '*' delimiter entirely)
    link = _make_link_with_chunks([corrupted, b""])
    frame = link.read_frame(deadline_s=0.3)
    assert frame is None
    assert link.frames_bad >= 1


def test_read_sensors_serial_no_port_falls_back_loudly():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        row = read_sensors_serial(0.0, None)
    assert row["data_source"] == "simulated"
    assert any(issubclass(w.category, FallbackToSimulation) for w in caught)


def test_read_sensors_serial_returns_hardware_data_when_frame_available():
    frame_bytes = encode_frame(seq=5, millis=5000, values=SAMPLE_VALUES)
    link = _make_link_with_chunks([frame_bytes])
    row = read_sensors_serial(0.0, "/dev/fake", link=link)
    assert row["data_source"] == "hardware"
    assert row["frame_seq"] == 5
    assert row["p_feed_bar"] == pytest.approx(0.5)


def test_read_sensors_serial_falls_back_loudly_when_no_frame_arrives():
    link = _make_link_with_chunks([b"", b"", b""])  # simulate timeout, no data ever
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        row = read_sensors_serial(0.0, "/dev/fake", link=link)
    assert row["data_source"] == "simulated"
    assert row["serial_port"] == "/dev/fake"
    assert any(issubclass(w.category, FallbackToSimulation) for w in caught)
