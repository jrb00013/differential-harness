#!/usr/bin/env python3
"""Real serial sensor ingestion for the CHORUS-SGH-1 bench DAQ.

Talks to a bench sensor node (DAQ-001: Raspberry Pi 4 + MCP3008 ADC HAT,
per hardware/bom/SGH1_BOM.csv) over a USB-CDC serial link using the
framed, checksummed ASCII protocol defined in daq/protocol.py.

Behavior contract:
  * If --port is given, this module genuinely attempts to open it with
    pyserial and read real, checksum-validated frames.
  * On a dropped connection it reconnects with backoff, up to a bounded
    number of attempts, rather than giving up silently.
  * It falls back to simulated data (daq.logger.read_sensors_sim) ONLY
    when the port cannot be opened at all, or no valid frame arrives
    within the configured read timeout after retries -- and every such
    fallback emits a loud, repeated warning (stderr + logging), never a
    silent substitution.
  * Malformed/corrupted frames are counted and logged, not silently
    accepted or silently dropped without trace.
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
import warnings
from pathlib import Path

from daq.logger import DATA, read_sensors_sim, run  # noqa: F401 (run kept for API parity)
from daq.protocol import SENTENCE_ID, VISION_SENTENCE_ID, Frame, FrameError, StreamReassembler

log = logging.getLogger("daq.serial_sensors")

try:
    import serial  # pyserial
    from serial import SerialException
except ImportError:  # pragma: no cover - exercised only when pyserial truly absent
    serial = None
    SerialException = Exception


DEFAULT_BAUD = 115200
CONNECT_TIMEOUT_S = 3.0
READ_TIMEOUT_S = 5.0
RECONNECT_ATTEMPTS = 3
RECONNECT_BACKOFF_S = 1.0


class FallbackToSimulation(RuntimeWarning):
    """Raised as a warning (not silently) whenever real hardware data is unavailable."""


def _warn_fallback(reason: str) -> None:
    msg = (
        f"[daq.serial_sensors] FALLING BACK TO SIMULATED DATA: {reason}. "
        "No real sensor data is being recorded for this sample."
    )
    warnings.warn(msg, FallbackToSimulation, stacklevel=3)
    log.warning(msg)
    print(f"WARNING: {msg}", file=sys.stderr)


class SerialLink:
    """Owns a pyserial connection plus frame reassembly and reconnect logic."""

    def __init__(
        self,
        port: str,
        baud: int = DEFAULT_BAUD,
        connect_timeout: float = CONNECT_TIMEOUT_S,
        read_timeout: float = READ_TIMEOUT_S,
        reconnect_attempts: int = RECONNECT_ATTEMPTS,
        reconnect_backoff: float = RECONNECT_BACKOFF_S,
    ) -> None:
        if serial is None:
            raise RuntimeError(
                "pyserial is not installed; install it with `pip install pyserial` "
                "to use real serial ingestion"
            )
        self.port = port
        self.baud = baud
        self.connect_timeout = connect_timeout
        self.read_timeout = read_timeout
        self.reconnect_attempts = reconnect_attempts
        self.reconnect_backoff = reconnect_backoff
        self._reasm = StreamReassembler()
        self._conn: "serial.Serial | None" = None
        self.frames_ok = 0
        self.frames_bad = 0
        self._pending: list[Frame] = []  # frames read but not yet consumed by the caller

    def open(self) -> bool:
        """Attempt to open the serial port. Returns True on success, False otherwise."""
        try:
            self._conn = serial.Serial(
                port=self.port,
                baudrate=self.baud,
                timeout=self.read_timeout,
                write_timeout=self.connect_timeout,
            )
            log.info("Opened serial port %s @ %d baud", self.port, self.baud)
            return True
        except (SerialException, OSError) as exc:
            log.error("Failed to open serial port %s: %s", self.port, exc)
            self._conn = None
            return False

    def close(self) -> None:
        if self._conn is not None:
            try:
                self._conn.close()
            except Exception:  # pragma: no cover - best-effort close
                pass
            self._conn = None

    def _reconnect(self) -> bool:
        for attempt in range(1, self.reconnect_attempts + 1):
            log.warning(
                "Serial link to %s lost; reconnect attempt %d/%d",
                self.port,
                attempt,
                self.reconnect_attempts,
            )
            self.close()
            time.sleep(self.reconnect_backoff * attempt)
            if self.open():
                return True
        return False

    def read_frame(self, deadline_s: float | None = None, sentence_id: str | None = None) -> Frame | None:
        """Block (up to deadline_s, or self.read_timeout if None) for one valid frame.

        The serial link multiplexes multiple sentence types ($SGH1 process
        sensors, $SGHV vision-stack sensors) on one connection. If
        `sentence_id` is given, only a frame of that type is returned;
        frames of other types encountered while waiting are buffered in
        `self._pending` so a subsequent call (for the other sentence id)
        can still consume them without re-reading the port.

        Returns None if the deadline elapses without a matching valid
        frame (caller should then fall back to simulation with an
        explicit warning).
        """
        if self._conn is None:
            return None

        for i, frame in enumerate(self._pending):
            if sentence_id is None or frame.sentence_id == sentence_id:
                return self._pending.pop(i)

        deadline = time.monotonic() + (deadline_s if deadline_s is not None else self.read_timeout)
        while time.monotonic() < deadline:
            try:
                raw = self._conn.readline()
            except (SerialException, OSError) as exc:
                log.error("Serial read error on %s: %s", self.port, exc)
                if not self._reconnect():
                    return None
                continue

            if not raw:
                # readline() timed out with no data -- keep waiting until deadline
                continue

            for result in self._reasm.feed(raw):
                if isinstance(result, FrameError):
                    self.frames_bad += 1
                    log.warning("Dropped malformed frame from %s: %s", self.port, result)
                    continue
                self.frames_ok += 1
                if sentence_id is None or result.sentence_id == sentence_id:
                    return result
                self._pending.append(result)  # not the type we're waiting for; save it
        return None


def read_sensors_serial(
    t: float,
    port: str | None,
    link: SerialLink | None = None,
) -> dict[str, float]:
    """Return one sensor row, sourced from real hardware when possible.

    `link` may be pre-opened by the caller (e.g. main()) so a single
    SerialLink/connection is reused across samples instead of reopening
    the port every call.
    """
    if not port:
        _warn_fallback("no --port configured")
        row = read_sensors_sim(t)
        row["data_source"] = "simulated"
        return row

    if link is None or link._conn is None:
        _warn_fallback(f"could not open or maintain serial port {port!r}")
        row = read_sensors_sim(t)
        row["data_source"] = "simulated"
        row["serial_port"] = port
        return row

    frame = link.read_frame(sentence_id=SENTENCE_ID)
    if frame is None:
        _warn_fallback(
            f"no valid $SGH1 frame received from {port!r} within {link.read_timeout}s "
            f"(ok={link.frames_ok}, bad={link.frames_bad})"
        )
        row = read_sensors_sim(t)
        row["data_source"] = "simulated"
        row["serial_port"] = port
        return row

    row = dict(frame.values)
    row["data_source"] = "hardware"
    row["serial_port"] = port
    row["frame_seq"] = frame.seq
    return row


def _vision_sensors_sim(t: float) -> dict[str, float]:
    """Simulated fallback for the vision-stack ($SGHV) sensor node.

    There is no real acoustic/vortex hardware attached in this
    environment (docs/ROADMAP.md M7); this is a clearly-labeled
    simulated placeholder consistent in shape with daq.protocol's
    VISION_FIELD_NAMES, used only so downstream tooling has a value to
    consume when no vision-stack node answers.
    """
    import math

    return {
        "us_amplitude_mV": 250.0 + 15.0 * math.sin(t / 9),
        "us_phase_deg": 0.0,
        "piezo_array_V": 1.2 + 0.1 * math.sin(t / 6),
    }


def read_vision_sensors_serial(
    t: float,
    port: str | None,
    link: SerialLink | None = None,
) -> dict[str, float]:
    """Return one $SGHV (vision-stack) sensor row, sourced from real
    hardware when possible, falling back loudly to simulation otherwise.

    Mirrors read_sensors_serial's contract exactly, but for the
    AEH-003 ultrasonic transducer / AEH-002 PVDF piezo array sentence.
    """
    if not port:
        _warn_fallback("no --port configured for vision-stack sensor node")
        row = _vision_sensors_sim(t)
        row["data_source"] = "simulated"
        return row

    if link is None or link._conn is None:
        _warn_fallback(f"could not open or maintain serial port {port!r} for vision-stack node")
        row = _vision_sensors_sim(t)
        row["data_source"] = "simulated"
        row["serial_port"] = port
        return row

    frame = link.read_frame(sentence_id=VISION_SENTENCE_ID)
    if frame is None:
        _warn_fallback(
            f"no valid $SGHV frame received from {port!r} within {link.read_timeout}s "
            f"(ok={link.frames_ok}, bad={link.frames_bad})"
        )
        row = _vision_sensors_sim(t)
        row["data_source"] = "simulated"
        row["serial_port"] = port
        return row

    row = dict(frame.values)
    row["data_source"] = "hardware"
    row["serial_port"] = port
    row["frame_seq"] = frame.seq
    return row


def main() -> None:
    p = argparse.ArgumentParser(description="Real (or explicitly-fallback) serial sensor logger")
    p.add_argument("--port", type=str, default=None, help="e.g. /dev/ttyUSB0")
    p.add_argument("--baud", type=int, default=DEFAULT_BAUD)
    p.add_argument("--duration", type=float, default=60)
    p.add_argument("--interval", type=float, default=1.0)
    p.add_argument("--read-timeout", type=float, default=READ_TIMEOUT_S)
    args = p.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    stamp = time.strftime("%Y%m%d_%H%M%S")
    out = DATA / f"serial_{stamp}.csv"

    link: SerialLink | None = None
    if args.port:
        try:
            link = SerialLink(args.port, baud=args.baud, read_timeout=args.read_timeout)
            if not link.open():
                _warn_fallback(f"failed to open {args.port!r} at startup")
                link = None
        except RuntimeError as exc:
            _warn_fallback(str(exc))
            link = None

    t0 = time.monotonic()
    import csv

    fields = list(read_sensors_sim(0).keys()) + [
        "iso_time",
        "serial_port",
        "data_source",
        "frame_seq",
    ]
    DATA.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        while time.monotonic() - t0 < args.duration:
            t = time.monotonic() - t0
            from datetime import datetime, timezone

            row = read_sensors_serial(t, args.port, link=link)
            row["iso_time"] = datetime.now(timezone.utc).isoformat()
            w.writerow(row)
            f.flush()
            time.sleep(args.interval)

    if link is not None:
        link.close()
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
