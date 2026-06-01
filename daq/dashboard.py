#!/usr/bin/env python3
"""Live plot of latest bench CSV (or sim)."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("csv", type=Path)
    args = p.parse_args()
    df = pd.read_csv(args.csv)
    fig, axes = plt.subplots(2, 2, figsize=(10, 6))
    axes[0, 0].plot(df["t_s"], df["P_draw_bar"], label="draw")
    axes[0, 0].plot(df["t_s"], df["P_feed_bar"], label="feed")
    axes[0, 0].set_ylabel("bar"); axes[0, 0].legend()
    axes[0, 1].plot(df["t_s"], df["P_elec_W"], color="C2")
    axes[0, 1].set_ylabel("W")
    axes[1, 0].plot(df["t_s"], df["cond_feed_mS_cm"], label="feed")
    axes[1, 0].plot(df["t_s"], df["cond_draw_mS_cm"], label="draw")
    axes[1, 0].set_ylabel("mS/cm"); axes[1, 0].legend()
    axes[1, 1].plot(df["t_s"], df["Q_feed_L_min"])
    axes[1, 1].set_ylabel("L/min feed")
    fig.suptitle("CHORUS-SGH-1 Bench")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
