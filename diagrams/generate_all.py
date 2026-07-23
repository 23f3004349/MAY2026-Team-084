"""
Generate all four SocietyEase diagrams (PNG + SVG) into ./output/.

Usage:
    python generate_all.py
"""
import sys
import time
from pathlib import Path

# Ensure this folder is importable when run from anywhere.
sys.path.insert(0, str(Path(__file__).parent))

import class_diagram
import component_design
import gantt_chart
import kanban_board

STEPS = [
    ("Class diagram      (graphviz)", class_diagram.main),
    ("Component design   (graphviz)", component_design.main),
    ("Gantt chart        (matplotlib)", gantt_chart.main),
    ("Kanban board       (matplotlib)", kanban_board.main),
]


def main():
    out = Path(__file__).parent / "output"
    out.mkdir(exist_ok=True)
    print(f"Generating SocietyEase diagrams -> {out}\n")
    start = time.perf_counter()
    for label, fn in STEPS:
        print(f"[*] {label}")
        fn()
    dt = time.perf_counter() - start
    files = sorted(p.name for p in out.glob("*") if p.suffix in (".png", ".svg"))
    print(f"\nDone in {dt:.1f}s. {len(files)} files:")
    for f in files:
        print(f"    output/{f}")


if __name__ == "__main__":
    main()
