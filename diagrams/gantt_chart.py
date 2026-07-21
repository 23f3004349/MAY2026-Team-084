"""
Gantt chart for SocietyEase - generated with matplotlib.

Renders the official 6-phase project schedule (see data.GANTT_TASKS). Each bar is
coloured Done / In progress / Planned, derived from TODAY, with a "Today" marker
and per-bar date ranges. Outputs PNG + SVG to ./output/.
"""
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

from data import GANTT_TASKS, TODAY, PROJECT_TITLE, TEAM

OUTPUT_DIR = Path(__file__).parent / "output"

STATUS_COLORS = {"done": "#16a34a", "in_progress": "#f59e0b", "planned": "#3b82f6"}
STATUS_LABEL = {"done": "Done", "in_progress": "In progress", "planned": "Planned"}
TODAY_COLOR = "#dc2626"


def _dt(s):
    return datetime.strptime(s, "%Y-%m-%d")


def _status(start, end, today):
    if end < today:
        return "done"
    if start <= today <= end:
        return "in_progress"
    return "planned"


def build():
    today = _dt(TODAY)
    n = len(GANTT_TASKS)
    fig, ax = plt.subplots(figsize=(14, 0.72 * n + 3))

    used = []
    for i, (task, s, e) in enumerate(GANTT_TASKS):
        sd, ed = _dt(s), _dt(e)
        start_n = mdates.date2num(sd)
        width = mdates.date2num(ed) - start_n + 1  # inclusive of the end day
        status = _status(sd, ed, today)
        used.append(status)

        if i % 2 == 0:                                   # subtle zebra striping
            ax.axhspan(i - 0.5, i + 0.5, color="#f8fafc", zorder=0)
        ax.barh(i, width, left=start_n, height=0.5, color=STATUS_COLORS[status],
                edgecolor="white", linewidth=1.2, zorder=3)

        label = f"{sd.strftime('%d %b')} – {ed.strftime('%d %b')}"
        ax.text(start_n + width + 1.2, i, label, va="center", ha="left",
                fontsize=8.5, color="#64748b", zorder=4)

    ax.set_yticks(range(n))
    ax.set_yticklabels([t[0] for t in GANTT_TASKS], fontsize=10)
    ax.invert_yaxis()

    ax.xaxis_date()
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax.xaxis.set_minor_locator(mdates.DayLocator())
    starts = [mdates.date2num(_dt(t[1])) for t in GANTT_TASKS]
    ends = [mdates.date2num(_dt(t[2])) for t in GANTT_TASKS]
    ax.set_xlim(min(starts) - 2, max(ends) + 16)

    # Today marker.
    tn = mdates.date2num(today)
    ax.axvline(tn, color=TODAY_COLOR, linestyle="--", linewidth=1.6, zorder=5)
    ax.text(tn + 0.4, -0.85, f"Today  {today.strftime('%d %b %Y')}",
            color=TODAY_COLOR, fontsize=9, ha="left", va="center", fontweight="bold")

    ax.grid(axis="x", linestyle=":", color="#cbd5e1", zorder=1)
    ax.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.tick_params(axis="y", length=0)

    ax.set_title(f"{PROJECT_TITLE}\nProject Gantt Chart  -  {TEAM}",
                 fontsize=15, fontweight="bold", pad=16)

    handles = [Patch(color=STATUS_COLORS[st], label=STATUS_LABEL[st])
               for st in ("done", "in_progress", "planned") if st in used]
    handles.append(Line2D([0], [0], color=TODAY_COLOR, linestyle="--", label="Today"))
    ax.legend(handles=handles, loc="upper right", fontsize=9, framealpha=0.95)

    fig.tight_layout()
    return fig


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    fig = build()
    for fmt in ("png", "svg"):
        path = OUTPUT_DIR / f"gantt_chart.{fmt}"
        fig.savefig(path, dpi=150, bbox_inches="tight",
                    facecolor="white" if fmt == "png" else "none")
        print(f"  wrote {path}")
    plt.close(fig)


if __name__ == "__main__":
    main()
