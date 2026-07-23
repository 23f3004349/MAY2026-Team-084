"""
Class diagram for SocietyEase - generated with Graphviz.

Renders all 19 SQLAlchemy models (models.py) as UML-style class boxes grouped by
domain, with cardinality-labelled relationships. Outputs PNG + SVG to ./output/.
"""
import os
import html
from pathlib import Path

# Make the Graphviz `dot` binary discoverable on Windows even if not on PATH.
_GV_BIN = r"C:\Program Files\Graphviz\bin"
if os.name == "nt" and os.path.isdir(_GV_BIN):
    os.environ["PATH"] = _GV_BIN + os.pathsep + os.environ.get("PATH", "")

import graphviz

from data import (
    MODELS, DOMAINS, STRONG_RELS, REF_RELS, PROJECT_TITLE, TEAM,
)

OUTPUT_DIR = Path(__file__).parent / "output"


def _html_label(name, meta):
    """Build an HTML-like Graphviz label: a UML class box with typed fields."""
    header, fill = DOMAINS[meta["domain"]]
    rows = [
        f'<TR><TD BGCOLOR="{header}" ALIGN="CENTER">'
        f'<FONT COLOR="white" POINT-SIZE="14"><B>{name}</B></FONT></TD></TR>',
        f'<TR><TD BGCOLOR="{fill}" ALIGN="CENTER">'
        f'<FONT COLOR="#64748b" POINT-SIZE="9"><I>{meta["table"]}</I></FONT></TD></TR>',
    ]
    for field, ftype, key in meta["fields"]:
        if key == "PK":
            mark = '&nbsp;<FONT COLOR="#b45309"><B>PK</B></FONT>'
        elif key == "FK":
            mark = '&nbsp;<FONT COLOR="#2563eb"><B>FK</B></FONT>'
        elif key == "U":
            mark = '&nbsp;<FONT COLOR="#7c3aed"><B>U</B></FONT>'
        else:
            mark = ""
        # Field text is user data -> escape <, >, & so bare "->" etc. don't
        # break Graphviz's HTML-like label parser.
        f_field = html.escape(field, quote=False)
        f_type = html.escape(ftype, quote=False)
        if ftype == "constraint":
            cell = (f'<FONT POINT-SIZE="9" COLOR="#94a3b8"><I>{f_field}</I></FONT>')
        else:
            cell = (f'<FONT POINT-SIZE="10">{f_field}</FONT>'
                    f'<FONT POINT-SIZE="10" COLOR="#64748b"> : {f_type}</FONT>{mark}')
        rows.append(f'<TR><TD BGCOLOR="{fill}" ALIGN="LEFT">{cell}</TD></TR>')
    inner = "".join(rows)
    return (f'<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" '
            f'CELLPADDING="4">{inner}</TABLE>>')


def build():
    g = graphviz.Digraph("class_diagram")
    g.attr(
        rankdir="TB", splines="spline", overlap="false", nodesep="0.45",
        ranksep="1.0", bgcolor="white", fontname="Helvetica", dpi="150",
        pad="0.4", compound="true",
        label=(f'<<FONT POINT-SIZE="22"><B>{PROJECT_TITLE}</B></FONT>'
               f'<BR/><FONT POINT-SIZE="13" COLOR="#64748b">'
               f'Class Diagram &#8226; 19 models &#8226; {TEAM}</FONT>>'),
        labelloc="t",
    )
    g.attr("node", shape="plaintext", fontname="Helvetica")
    g.attr("edge", fontname="Helvetica", fontsize="9")

    # One cluster per domain.
    for idx, (domain, (header, fill)) in enumerate(DOMAINS.items()):
        with g.subgraph(name=f"cluster_{idx}") as c:
            c.attr(label=domain, style="rounded,filled", color=header,
                   fillcolor="#fbfcfe", fontcolor=header, fontsize="15",
                   penwidth="2.0", margin="12")
            for name, meta in MODELS.items():
                if meta["domain"] == domain:
                    c.node(name, label=_html_label(name, meta))

    # Strong relationships (back_populates + cascade / 1-1): solid edges.
    for parent, child, pcard, ccard, label in STRONG_RELS:
        g.edge(
            parent, child, label=f"  {label}  ",
            taillabel=pcard, headlabel=ccard,
            color="#334155", penwidth="1.5", arrowhead="vee",
            arrowtail="odiamond", dir="both", labeldistance="1.6",
            labelfontsize="11", fontcolor="#334155",
        )

    # FK reference edges (creator / assignee / logger, etc.): dashed, non-ranking.
    for src, dst, role in REF_RELS:
        g.edge(
            src, dst, label=role, style="dashed", color="#94a3b8",
            fontcolor="#94a3b8", fontsize="8", arrowhead="vee",
            constraint="false", penwidth="1.0",
        )

    # Legend — styled rounded card.
    F = "Helvetica"

    def ft(text, color=None, size="10", bold=False):
        attrs = f' FACE="{F}" POINT-SIZE="{size}"' + (f' COLOR="{color}"' if color else "")
        body = f"<B>{text}</B>" if bold else text
        return f"<FONT{attrs}>{body}</FONT>"

    def chip(text, color):
        return (f'<TD STYLE="ROUNDED" BGCOLOR="{color}" CELLPADDING="3">'
                f'{ft(" " + text + " ", "white", "9", True)}</TD>')

    div = ('<TR><TD COLSPAN="2" HEIGHT="2" CELLPADDING="0" '
           'BGCOLOR="#e2e8f0"></TD></TR>')

    legend = (
        '<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="5">'
        f'<TR><TD COLSPAN="2" ALIGN="CENTER">{ft("Legend", "#0f172a", "14", True)}'
        '</TD></TR>'
        + div +
        f'<TR><TD ALIGN="CENTER">{ft("&#8212;&#8212;&#8212;", "#334155", "14", True)}'
        f'</TD><TD ALIGN="LEFT">{ft("solid  =  owns / composition (back_populates + cascade delete)")}'
        '</TD></TR>'
        f'<TR><TD ALIGN="CENTER">{ft("- - -", "#94a3b8", "14", True)}'
        f'</TD><TD ALIGN="LEFT">{ft("dashed  =  FK reference to User / Apartment (creator, assignee, ...)")}'
        '</TD></TR>'
        + div +
        '<TR><TD COLSPAN="2" ALIGN="LEFT">'
        '<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5" CELLPADDING="0"><TR>'
        + chip("PK", "#b45309") + f'<TD>{ft("primary key")}</TD>'
        + chip("FK", "#2563eb") + f'<TD>{ft("foreign key")}</TD>'
        + chip("U", "#7c3aed") + f'<TD>{ft("unique")}</TD>'
        '</TR></TABLE></TD></TR>'
        + div +
        '<TR><TD COLSPAN="2" ALIGN="LEFT">'
        f'{ft("1 to * cardinality  &#8226;  User &lt;-&gt; Vote is many-to-many via ")}'
        f'{ft("VoteResponse", "#7c3aed", "10", True)}{ft(" (association object)")}'
        '</TD></TR>'
        '</TABLE>>'
    )
    g.node("legend", label=legend, shape="box", style="rounded,filled",
           fillcolor="#f8fafc", color="#e2e8f0", penwidth="1.3", margin="0.18,0.12")
    return g


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    g = build()
    stem = str(OUTPUT_DIR / "class_diagram")
    for fmt in ("png", "svg"):
        g.format = fmt
        path = g.render(stem, cleanup=True)
        print(f"  wrote {path}")


if __name__ == "__main__":
    main()
