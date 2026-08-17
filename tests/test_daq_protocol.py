"""Unit tests for daq/protocol.py using synthetic byte streams (no hardware)."""

from __future__ import annotations

from daq.protocol import (
    FIELD_NAMES,
    FrameError,
    StreamReassembler,
    checksum,
    encode_frame,
    parse_frame,
)

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


def test_encode_then_parse_round_trips():
    frame_bytes = encode_frame(seq=1, millis=1000, values=SAMPLE_VALUES)
    line = frame_bytes.decode("ascii")
    frame = parse_frame(line)
    assert frame.seq == 1
    assert frame.millis == 1000
    for name in FIELD_NAMES:
        assert frame.values[name] == pytest_approx(SAMPLE_VALUES[name])


def pytest_approx(x, tol=1e-6):
    class _Approx(float):
        def __eq__(self, other):
            return abs(other - x) <= tol

    return _Approx(x)


def test_checksum_matches_nmea_style_xor():
    payload = "SGH1,1,1000,0.5"
    cs = checksum(payload)
    expected = 0
    for ch in payload:
        expected ^= ord(ch)
    assert cs == f"{expected:02X}"


def test_parse_frame_rejects_bad_checksum():
    frame_bytes = encode_frame(seq=2, millis=2000, values=SAMPLE_VALUES)
    line = frame_bytes.decode("ascii").strip()
    # flip the checksum
    body, _, cs = line[1:].partition("*")
    bad_line = f"${body}*00"
    if cs == "00":
        bad_line = f"${body}*FF"
    try:
        parse_frame(bad_line)
        assert False, "expected FrameError"
    except FrameError:
        pass


def test_parse_frame_rejects_missing_dollar():
    try:
        parse_frame("SGH1,1,1000*00")
        assert False, "expected FrameError"
    except FrameError:
        pass


def test_parse_frame_rejects_wrong_field_count():
    try:
        parse_frame("$SGH1,1,1000,0.5*00")
        assert False, "expected FrameError"
    except FrameError:
        pass


def test_reassembler_handles_split_frame_across_reads():
    frame_bytes = encode_frame(seq=3, millis=3000, values=SAMPLE_VALUES)
    reasm = StreamReassembler()
    part_a = frame_bytes[:10]
    part_b = frame_bytes[10:]

    results_a = reasm.feed(part_a)
    assert results_a == []  # no newline yet, nothing to yield

    results_b = reasm.feed(part_b)
    assert len(results_b) == 1
    assert not isinstance(results_b[0], FrameError)
    assert results_b[0].seq == 3


def test_reassembler_reports_garbled_frame_without_dropping_stream():
    reasm = StreamReassembler()
    good = encode_frame(seq=4, millis=4000, values=SAMPLE_VALUES)
    garbage = b"NOISE-NOT-A-FRAME\r\n"
    results = reasm.feed(garbage + good)
    assert len(results) == 2
    assert isinstance(results[0], FrameError)
    assert not isinstance(results[1], FrameError)
    assert results[1].seq == 4


def test_reassembler_skips_leading_garbage_before_dollar_on_same_line():
    reasm = StreamReassembler()
    good = encode_frame(seq=5, millis=5000, values=SAMPLE_VALUES).decode("ascii")
    noisy_line = ("\x00\x01" + good).encode("ascii", errors="ignore")
    results = reasm.feed(noisy_line)
    assert len(results) == 1
    assert not isinstance(results[0], FrameError)
    assert results[0].seq == 5
