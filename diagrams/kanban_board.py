"""
Kanban board for SocietyEase - generated with matplotlib.

Three columns (Done / In Progress / To Do) reflecting the real repo state:
backend + auth + a few screens are done; the announcements edit flow and the
Home dashboard are in progress; the remaining feature UIs are still to do.
Outputs PNG + SVG to ./output/.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

from data import KANBAN, KANBAN_COLORS, PROJECT_TITLE, TEAM

OUTPUT_DIR = Path(__file__).parent / "output"

COLS = ["Done", "In Progress", "To Do"]
COL_W = 3.4
COL_GAP = 0.5
HEADER_H = 0.95
CARD_GAP = 0.22
CARD_PAD_TOP = 0.35


def _lines(txt):
    return txt.count("\n") + 1


def _card_h(txt):
    return 0.5 + 0.3 * _lines(txt)


def build():
    # Height needed per column, take the tallest.
    col_heights = []
    for c in COLS:
        h = HEADER_H + CARD_PAD_TOP
        for card, _ in KANBAN[c]:
            h += _card_h(card) + CARD_GAP
        col_heights.append(h)
    H = max(col_heights)
    W = len(COLS) * COL_W + (len(COLS) - 1) * COL_GAP

    fig, ax = plt.subplots(figsize=(W * 1.25, H * 0.66 + 1))
    ax.set_xlim(-0.3, W + 0.3)
    ax.set_ylim(0, H + 1.0)
    ax.axis("off")

    # Title.
    ax.text(W / 2, H + 0.7, PROJECT_TITLE, ha="center", va="center",
            fontsize=15, fontweight="bold", color="#0f172a")
    ax.text(W / 2, H + 0.3, f"Kanban Board  •  {TEAM}", ha="center",
            va="center", fontsize=11, color="#64748b")

    top_y = H

    for i, c in enumerate(COLS):
        x0 = i * (COL_W + COL_GAP)
        header, fill = KANBAN_COLORS[c]

        # Column background.
        ax.add_patch(Rectangle((x0, 0), COL_W, H, facecolor=fill,
                               edgecolor="#e2e8f0", linewidth=1, alpha=0.5,
                               zorder=0))

        # Column header.
        hy = top_y - HEADER_H
        ax.add_patch(FancyBboxPatch(
            (x0 + 0.1, hy), COL_W - 0.2, HEADER_H - 0.15,
            boxstyle="round,pad=0.02,rounding_size=0.1",
            facecolor=header, edgecolor="none", zorder=2))
        ax.text(x0 + COL_W / 2, hy + (HEADER_H - 0.15) / 2,
                f"{c}   ({len(KANBAN[c])})", ha="center", va="center",
                color="white", fontsize=13, fontweight="bold", zorder=3)

        # Cards.
        y = hy - CARD_GAP
        for card, owner in KANBAN[c]:
            ch = _card_h(card)
            y -= ch
            ax.add_patch(FancyBboxPatch(
                (x0 + 0.15, y), COL_W - 0.3, ch - 0.06,
                boxstyle="round,pad=0.02,rounding_size=0.06",
                facecolor="white", edgecolor=header, linewidth=1.3, zorder=2))
            ax.text(x0 + 0.32, y + ch - 0.06 - 0.16, card, ha="left", va="top",
                    fontsize=9.5, color="#1e293b", zorder=3)
            if owner:
                ax.text(x0 + COL_W - 0.32, y + 0.13, owner, ha="right",
                        va="bottom", fontsize=7.5, color=header,
                        style="italic", zorder=3)
            y -= CARD_GAP

    return fig


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    fig = build()
    for fmt in ("png", "svg"):
        path = OUTPUT_DIR / f"kanban_board.{fmt}"
        fig.savefig(path, dpi=150, bbox_inches="tight",
                    facecolor="white" if fmt == "png" else "none")
        print(f"  wrote {path}")
    plt.close(fig)


if __name__ == "__main__":
    main()
