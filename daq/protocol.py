#!/usr/bin/env python3
"""Wire protocol for the SGH-1 bench telemetry serial link.

Framing (NMEA-style ASCII, matches the DAQ-001 Pi/ADC-HAT -> USB-CDC
serial link implied by hardware/bom/SGH1_BOM.csv):

    $SGH1,<seq>,<millis>,<p_feed_bar>,<p_draw_bar>,<q_feed_L_min>,
    <q_draw_L_min>,<cond_feed_mS_cm>,<cond_draw_mS_cm>,<t_feed_C>,
    <t_draw_C>,<p_elec_W>*<checksum_hex>\r\n

A second sentence type multiplexed on the same link carries the
acoustic/vortex "vision stack" sensors (AEH-003 28kHz ultrasonic
transducer + AEH-002 PVDF piezo array):

    $SGHV,<seq>,<millis>,<us_amplitude_mV>,<us_phase_deg>,
    <piezo_array_V>*<checksum_hex>\r\n

`<checksum_hex>` is the 2-digit uppercase hex XOR of every byte between
`$` and `*` (exclusive), the same scheme NMEA-0183 uses, chosen because
it is trivial to implement on a microcontroller and cheap to verify on
the host. This module contains ONLY parsing/framing logic so it can be
unit tested with synthetic byte streams — no serial I/O here.
"""

from __future__ import annotations

from dataclasses import dataclass

SENTENCE_ID = "SGH1"

FIELD_NAMES = [
    "p_feed_bar",
    "p_draw_bar",
    "q_feed_L_min",
    "q_draw_L_min",
    "cond_feed_mS_cm",
    "cond_draw_mS_cm",
    "t_feed_C",
    "t_draw_C",
    "p_elec_W",
]

N_FIELDS = len(FIELD_NAMES)

# Second sentence type: the acoustic/vortex "vision stack" sensor node
# (AEH-003 28kHz ultrasonic transducer + AEH-002 PVDF piezo array, per
# hardware/bom/SGH1_BOM.csv). Kept as a distinct sentence id on the same
# wire/link so a single serial connection can multiplex both the core
# process sensors ($SGH1) and the vision-stack sensors ($SGHV).
VISION_SENTENCE_ID = "SGHV"

VISION_FIELD_NAMES = [
    "us_amplitude_mV",
    "us_phase_deg",
    "piezo_array_V",
]

N_VISION_FIELDS = len(VISION_FIELD_NAMES)

# Registry of known sentence specs, used by parse_any() to dispatch
# generically without the caller needing to know the sentence id ahead
# of time.
_SENTENCE_SPECS: dict[str, list[str]] = {
    SENTENCE_ID: FIELD_NAMES,
    VISION_SENTENCE_ID: VISION_FIELD_NAMES,
}


class FrameError(ValueError):
    """A frame was structurally invalid or failed checksum validation."""


@dataclass
class Frame:
    seq: int
    millis: int
    values: dict[str, float]
    sentence_id: str = SENTENCE_ID


def checksum(payload: str) -> str:
    """XOR checksum of all characters in payload, as 2-digit uppercase hex."""
    cs = 0
    for ch in payload:
        cs ^= ord(ch)
    return f"{cs:02X}"


def _encode(sentence_id: str, field_names: list[str], seq: int, millis: int, values: dict[str, float]) -> bytes:
    fields = [str(seq), str(millis)] + [f"{values[k]:.6g}" for k in field_names]
    payload = f"{sentence_id}," + ",".join(fields)
    cs = checksum(payload)
    return f"${payload}*{cs}\r\n".encode("ascii")


def encode_frame(seq: int, millis: int, values: dict[str, float]) -> bytes:
    """Build a wire frame for the core process-sensor ($SGH1) sentence."""
    return _encode(SENTENCE_ID, FIELD_NAMES, seq, millis, values)


def encode_vision_frame(seq: int, millis: int, values: dict[str, float]) -> bytes:
    """Build a wire frame for the vision-stack sensor ($SGHV) sentence
    (AEH-003 ultrasonic transducer + AEH-002 PVDF piezo array)."""
    return _encode(VISION_SENTENCE_ID, VISION_FIELD_NAMES, seq, millis, values)


def _parse(line: str, expected_sentence_id: str | None) -> Frame:
    """Parse and checksum-validate a single decoded sentence (no trailing CRLF).

    If `expected_sentence_id` is given, the parsed sentence id must match
    it. If None, any known sentence id in `_SENTENCE_SPECS` is accepted
    (used by `parse_any`).

    Raises FrameError on any structural or checksum problem.
    """
    line = line.strip()
    if not line.startswith("$"):
        raise FrameError(f"frame missing leading '$': {line!r}")
    if "*" not in line:
        raise FrameError(f"frame missing checksum delimiter '*': {line!r}")

    body, _, cs_given = line[1:].partition("*")
    cs_given = cs_given.strip().upper()
    if len(cs_given) != 2:
        raise FrameError(f"malformed checksum field: {line!r}")

    cs_calc = checksum(body)
    if cs_calc != cs_given:
        raise FrameError(f"checksum mismatch (got {cs_given}, expected {cs_calc}): {line!r}")

    parts = body.split(",")
    if not parts:
        raise FrameError(f"empty frame body: {line!r}")

    sentence_id = parts[0]
    if expected_sentence_id is not None:
        if sentence_id != expected_sentence_id:
            raise FrameError(f"unexpected sentence id: {line!r}")
        field_names = _SENTENCE_SPECS[expected_sentence_id]
    else:
        if sentence_id not in _SENTENCE_SPECS:
            raise FrameError(f"unknown sentence id {sentence_id!r}: {line!r}")
        field_names = _SENTENCE_SPECS[sentence_id]

    n_fields = len(field_names)
    if len(parts) != 3 + n_fields:
        raise FrameError(f"expected {3 + n_fields} comma fields, got {len(parts)}: {line!r}")

    try:
        seq = int(parts[1])
        millis = int(parts[2])
        values = {name: float(v) for name, v in zip(field_names, parts[3:])}
    except ValueError as exc:
        raise FrameError(f"non-numeric field in {line!r}: {exc}") from exc

    return Frame(seq=seq, millis=millis, values=values, sentence_id=sentence_id)


def parse_frame(line: str) -> Frame:
    """Parse a core process-sensor ($SGH1) sentence. Raises FrameError otherwise."""
    return _parse(line, expected_sentence_id=SENTENCE_ID)


def parse_vision_frame(line: str) -> Frame:
    """Parse a vision-stack sensor ($SGHV) sentence. Raises FrameError otherwise."""
    return _parse(line, expected_sentence_id=VISION_SENTENCE_ID)


def parse_any(line: str) -> Frame:
    """Parse either a $SGH1 or $SGHV sentence, dispatching on the sentence id."""
    return _parse(line, expected_sentence_id=None)


class StreamReassembler:
    """Buffers raw bytes from a serial port and yields complete, parsed frames.

    Handles: frames split across multiple reads, garbage bytes before the
    first '$', and CRLF or LF-only line endings. Malformed frames are
    surfaced as FrameError from `feed()` (caller decides whether to count
    and continue) rather than being silently dropped.
    """

    def __init__(self, max_buffer: int = 8192) -> None:
        self._buf = ""
        self._max_buffer = max_buffer

    def feed(self, data: bytes) -> list[Frame | FrameError]:
        """Feed newly-read bytes; return zero or more results (Frame or FrameError)."""
        try:
            self._buf += data.decode("ascii", errors="replace")
        except Exception:  # pragma: no cover - decode with errors="replace" won't raise
            return []

        results: list[Frame | FrameError] = []
        while "\n" in self._buf:
            line, self._buf = self._buf.split("\n", 1)
            line = line.strip("\r")
            if not line:
                continue
            # discard any garbage preceding the first '$' on this line
            dollar = line.find("$")
            if dollar == -1:
                results.append(FrameError(f"no frame start found: {line!r}"))
                continue
            line = line[dollar:]
            try:
                results.append(parse_any(line))
            except FrameError as exc:
                results.append(exc)

        if len(self._buf) > self._max_buffer:
            # runaway buffer with no newline (garbled link) - drop it
            self._buf = ""
            results.append(FrameError("buffer overflow without newline; buffer reset"))

        return results
