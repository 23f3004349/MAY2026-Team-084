"""
Component / architecture design for SocietyEase - generated with Graphviz.

Shows the layered architecture: Vue SPA -> Flask REST API (12 blueprints) ->
Flask-SQLAlchemy ORM -> SQLite, plus the cross-cutting JWT/CORS concerns.
Outputs PNG + SVG to ./output/.
"""
import os
from pathlib import Path

_GV_BIN = r"C:\Program Files\Graphviz\bin"
if os.name == "nt" and os.path.isdir(_GV_BIN):
    os.environ["PATH"] = _GV_BIN + os.pathsep + os.environ.get("PATH", "")

import graphviz

from data import (
    FRONTEND_SCREENS, BLUEPRINTS, WIRED_BLUEPRINTS, PROJECT_TITLE, TEAM,
)

OUTPUT_DIR = Path(__file__).parent / "output"


def build():
    g = graphviz.Digraph("component_design")
    g.attr(
        rankdir="TB", compound="true", bgcolor="white", fontname="Helvetica",
        dpi="150", pad="0.4", nodesep="0.35", ranksep="1.0", splines="spline",
        label=(f'<<FONT POINT-SIZE="22"><B>{PROJECT_TITLE}</B></FONT>'
               f'<BR/><FONT POINT-SIZE="13" COLOR="#64748b">'
               f'Component / Architecture Design &#8226; {TEAM}</FONT>>'),
        labelloc="t",
    )
    g.attr("node", shape="box", style="rounded,filled", fontname="Helvetica",
           fontsize="11", color="#cbd5e1", penwidth="1.2", fillcolor="#ffffff")
    g.attr("edge", fontname="Helvetica", fontsize="10", color="#475569")

    # ---- Client layer -----------------------------------------------------
    with g.subgraph(name="cluster_client") as c:
        c.attr(label="Client  -  Vue 3 SPA   (Vite - vue-router - axios - Bootstrap 5   @ localhost:5173)",
               style="rounded,filled", color="#2563eb", fillcolor="#eff6ff",
               fontcolor="#1e3a8a", fontsize="14", penwidth="2.0", margin="12")
        c.node("spa_entry", "index.html  ->  main.js  ->  App.vue\n<router-view>  (routes.js)",
               fillcolor="#dbeafe", color="#2563eb")
        for name, path in FRONTEND_SCREENS:
            c.node(f"scr_{name}", f"{name}\n{path}")
        c.node("navbar", "AssociationNavBar\n(shared component)")
        c.node("auth_js", "utils/auth.js\ngetApiBase() + token helpers",
               fillcolor="#fef9c3", color="#ca8a04")
        for name, _ in FRONTEND_SCREENS:
            c.edge("spa_entry", f"scr_{name}", style="invis")

    # ---- Cross-cutting ----------------------------------------------------
    with g.subgraph(name="cluster_cross") as c:
        c.attr(label="Cross-cutting", style="rounded,filled", color="#a855f7",
               fillcolor="#faf5ff", fontcolor="#6b21a8", fontsize="13",
               penwidth="2.0", margin="10")
        c.node("jwt", "JWTManager\n(flask-jwt-extended)\n@jwt_required - tokens never expire",
               fillcolor="#f3e8ff", color="#a855f7")
        c.node("cors", "Flask-CORS\norigin: localhost:5173",
               fillcolor="#f3e8ff", color="#a855f7")

    # ---- API layer --------------------------------------------------------
    with g.subgraph(name="cluster_api") as c:
        c.attr(label="REST API  -  Flask   (create_app() factory   @ localhost:5000,  /api/*)",
               style="rounded,filled", color="#16a34a", fillcolor="#f0fdf4",
               fontcolor="#14532d", fontsize="14", penwidth="2.0", margin="12")
        for name, prefix, resp in BLUEPRINTS:
            wired = name in WIRED_BLUEPRINTS
            c.node(
                f"bp_{name}", f"{name}\n{prefix}\n{resp}",
                fillcolor="#dcfce7" if wired else "#f8fafc",
                color="#16a34a" if wired else "#cbd5e1",
                penwidth="2.2" if wired else "1.0",
            )

    # ---- Domain / ORM layer ----------------------------------------------
    with g.subgraph(name="cluster_orm") as c:
        c.attr(label="Domain / ORM  -  Flask-SQLAlchemy   (models.py)",
               style="rounded,filled", color="#7c3aed", fillcolor="#f5f3ff",
               fontcolor="#5b21b6", fontsize="14", penwidth="2.0", margin="12")
        c.node("orm", "db = SQLAlchemy()  -  db.session\n(blueprints call the ORM directly;\nno service / repository layer)",
               fillcolor="#ede9fe", color="#7c3aed")
        c.node("models", "19 models\nUser - Apartment - Resident - Complaint - ComplaintUpdate\n"
                         "Invoice - Payment - Expense - MaintenanceTask - Announcement\n"
                         "Vote - VoteOption - VoteResponse - EmergencyContact\n"
                         "Equipment - EquipmentServiceLog - SocietyHealthScore\n"
                         "ConflictReport - ParkingSlot")
        c.edge("orm", "models", style="invis")

    # ---- Persistence ------------------------------------------------------
    g.node("db_sqlite", "SQLite\nsocietyease.db\n(db.create_all())",
           shape="cylinder", fillcolor="#e2e8f0", color="#475569", penwidth="1.6")

    # ---- Real wired calls (client -> API) : solid green -------------------
    wired_calls = [
        ("scr_LoginPage", "bp_auth", "POST /login"),
        ("scr_RegisterPage", "bp_auth", "POST /register"),
        ("scr_AssociationManager", "bp_notices", "GET / DELETE"),
        ("scr_AddAnnouncement", "bp_notices", "POST"),
    ]
    for src, dst, lbl in wired_calls:
        g.edge(src, dst, label=lbl, color="#16a34a", fontcolor="#166534",
               penwidth="1.8", arrowhead="vee")

    # auth.js attaches the JWT bearer header to every request.
    g.edge("auth_js", "bp_auth", lhead="cluster_api", style="dashed",
           color="#ca8a04", fontcolor="#a16207", label="attach JWT Bearer",
           constraint="false")

    # Cross-cutting attaches to the whole API layer.
    g.edge("jwt", "bp_members", lhead="cluster_api", style="dashed",
           color="#a855f7", fontcolor="#7e22ce", label="protect", constraint="false")
    g.edge("cors", "bp_members", lhead="cluster_api", style="dashed",
           color="#a855f7", fontcolor="#7e22ce", label="CORS", constraint="false")

    # API -> ORM -> DB (all blueprints use the ORM).
    g.edge("bp_notices", "orm", ltail="cluster_api", lhead="cluster_orm",
           label="  all blueprints -> db.session  ", color="#7c3aed",
           fontcolor="#5b21b6", penwidth="2.0")
    g.edge("models", "db_sqlite", ltail="cluster_orm",
           label="  SQLAlchemy Core -> SQL  ", color="#475569", penwidth="2.0")

    # ---- Legend — styled rounded card. -----------------------------------
    F = "Helvetica"

    def ft(text, color=None, size="10", bold=False):
        attrs = f' FACE="{F}" POINT-SIZE="{size}"' + (f' COLOR="{color}"' if color else "")
        body = f"<B>{text}</B>" if bold else text
        return f"<FONT{attrs}>{body}</FONT>"

    def box_swatch(fill, border):
        return (f'<TD FIXEDSIZE="TRUE" WIDTH="30" HEIGHT="18" STYLE="ROUNDED" '
                f'BGCOLOR="{fill}" BORDER="2" COLOR="{border}"></TD>')

    div = ('<TR><TD COLSPAN="2" HEIGHT="2" CELLPADDING="0" '
           'BGCOLOR="#e2e8f0"></TD></TR>')

    legend = (
        '<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="5">'
        f'<TR><TD COLSPAN="2" ALIGN="CENTER">{ft("Legend", "#0f172a", "14", True)}'
        '</TD></TR>'
        + div +
        f'<TR>{box_swatch("#dcfce7", "#16a34a")}<TD ALIGN="LEFT">'
        f'{ft("backend built ")}{ft("AND wired", "#166534", "10", True)}'
        f'{ft(" to a UI screen (auth, notices)")}</TD></TR>'
        f'<TR>{box_swatch("#f8fafc", "#cbd5e1")}<TD ALIGN="LEFT">'
        f'{ft("backend built, no frontend UI yet (10 of 12)")}</TD></TR>'
        + div +
        f'<TR><TD ALIGN="CENTER">{ft("&#8212;&#8212;&#8212;", "#16a34a", "14", True)}'
        f'</TD><TD ALIGN="LEFT">{ft("solid  =  actual HTTP call")}</TD></TR>'
        f'<TR><TD ALIGN="CENTER">{ft("- - -", "#a855f7", "14", True)}'
        f'</TD><TD ALIGN="LEFT">{ft("dashed  =  cross-cutting concern")}</TD></TR>'
        '</TABLE>>'
    )
    g.node("legend", label=legend, shape="box", style="rounded,filled",
           fillcolor="#f8fafc", color="#e2e8f0", penwidth="1.3", margin="0.18,0.12")
    return g


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    g = build()
    stem = str(OUTPUT_DIR / "component_design")
    for fmt in ("png", "svg"):
        g.format = fmt
        path = g.render(stem, cleanup=True)
        print(f"  wrote {path}")


if __name__ == "__main__":
    main()
