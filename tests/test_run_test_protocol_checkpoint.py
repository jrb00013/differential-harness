"""Tests for checkpointing/resume logic in scripts/run_test_protocol.py.

subprocess.run is mocked throughout -- these tests exercise the
checkpoint bookkeeping and resume skip-logic, not the real logger/daq
subprocess pipeline (which is covered by daq's own tests).
"""

from __future__ import annotations

from pathlib import Path

import scripts.run_test_protocol as rtp
from scripts.run_test_protocol import Checkpoint, run_t0


def test_checkpoint_round_trips_through_disk(tmp_path):
    ckpt_path = tmp_path / "checkpoint.json"
    ckpt = Checkpoint(ckpt_path)
    assert not ckpt.is_done("T0.leak")

    ckpt.mark_done("T0.leak", "some/path.csv")
    assert ckpt.is_done("T0.leak")
    assert ckpt.result("T0.leak") == "some/path.csv"

    # reload from disk -> state persists
    reloaded = Checkpoint(ckpt_path)
    assert reloaded.is_done("T0.leak")
    assert reloaded.result("T0.leak") == "some/path.csv"


def test_run_t0_resume_skips_completed_step(tmp_path, monkeypatch):
    calls: list[str] = []

    def fake_run(cmd, check, cwd):
        calls.append(cmd[cmd.index("--phase") + 1])

        class FakeCompleted:
            returncode = 0

        return FakeCompleted()

    monkeypatch.setattr(rtp.subprocess, "run", fake_run)

    out_dir = tmp_path / "T0_run"
    out_dir.mkdir()
    ckpt = Checkpoint(out_dir / "checkpoint.json")

    # First pass: both leak and ramp run.
    run_t0(out_dir, interval=1.0, ckpt=ckpt, resume=False)
    assert calls == ["leak", "ramp"]

    # Pre-seed checkpoint as if "leak" already completed, then resume:
    # only "ramp" should run again.
    calls.clear()
    ckpt2 = Checkpoint(out_dir / "checkpoint.json")
    assert ckpt2.is_done("T0.leak")
    assert ckpt2.is_done("T0.ramp")

    run_t0(out_dir, interval=1.0, ckpt=ckpt2, resume=True)
    assert calls == []  # both already done -> nothing re-run


def test_run_t0_resume_reruns_only_incomplete_step(tmp_path, monkeypatch):
    calls: list[str] = []

    def fake_run(cmd, check, cwd):
        calls.append(cmd[cmd.index("--phase") + 1])

        class FakeCompleted:
            returncode = 0

        return FakeCompleted()

    monkeypatch.setattr(rtp.subprocess, "run", fake_run)

    out_dir = tmp_path / "T0_partial"
    out_dir.mkdir()
    ckpt = Checkpoint(out_dir / "checkpoint.json")
    # Manually seed only "leak" as completed, simulating a crash after step 1.
    ckpt.mark_done("T0.leak", str(out_dir / "T0_leak.csv"))

    run_t0(out_dir, interval=1.0, ckpt=ckpt, resume=True)
    assert calls == ["ramp"]  # leak skipped, ramp re-run
