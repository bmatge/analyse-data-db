"""FastAPI application for budget data exploration."""

import os
import sqlite3
from pathlib import Path
from fastapi import FastAPI, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_PATH = PROJECT_ROOT / "db" / "budget.db"
STATIC_DIR = Path(__file__).parent / "static"

ENTRANTS_DIR = PROJECT_ROOT / "entrants"

app = FastAPI(title="Budget Explorer", version="0.1.0")


@app.middleware("http")
async def add_noindex_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Robots-Tag"] = "noindex, nofollow, nosnippet, noarchive"
    return response


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


# ── Pages ──────────────────────────────────────────────

@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/glossaire")
async def glossaire():
    return FileResponse(STATIC_DIR / "glossaire.html")


@app.get("/explorer")
async def explorer():
    return FileResponse(STATIC_DIR / "explorer.html")


@app.get("/corpus")
async def corpus():
    return FileResponse(STATIC_DIR / "corpus.html")


@app.get("/sankey")
async def sankey():
    return FileResponse(STATIC_DIR / "nomenclature.html")


@app.get("/nomenclature")
async def nomenclature():
    return FileResponse(STATIC_DIR / "nomenclature.html")


@app.get("/plf-lfi")
async def plf_lfi():
    return FileResponse(STATIC_DIR / "plf-lfi.html")


@app.get("/api-specs")
async def api_specs():
    return FileResponse(STATIC_DIR / "api-specs.html")


# ── API: metadata ──────────────────────────────────────

@app.get("/api/annees")
async def api_annees():
    """List available years."""
    conn = get_db()
    rows = conn.execute(
        "SELECT DISTINCT annee FROM programme ORDER BY annee"
    ).fetchall()
    conn.close()
    return [r["annee"] for r in rows]


@app.get("/api/stats/{annee}")
async def api_stats(annee: int):
    """Summary stats for a given year."""
    conn = get_db()
    stats = {}
    for table in ("mission", "programme", "action", "sous_action"):
        count = conn.execute(
            f"SELECT COUNT(*) as n FROM {table} WHERE annee = ?", (annee,)
        ).fetchone()["n"]
        stats[table + "s"] = count

    budget = conn.execute(
        "SELECT COUNT(*) as n, SUM(ae) as total_ae, SUM(cp) as total_cp "
        "FROM donnees_budget WHERE annee = ?", (annee,)
    ).fetchone()
    stats["lignes_budget"] = budget["n"]
    stats["total_ae"] = budget["total_ae"]
    stats["total_cp"] = budget["total_cp"]

    docs = conn.execute(
        "SELECT COUNT(*) as n FROM document WHERE annee = ?", (annee,)
    ).fetchone()["n"]
    stats["documents"] = docs

    conn.close()
    return stats


# ── API: nomenclature hierarchy ────────────────────────

@app.get("/api/types-budget")
async def api_types_budget():
    conn = get_db()
    rows = conn.execute("SELECT code, libelle FROM type_budget ORDER BY code").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/api/missions/{annee}")
async def api_missions(annee: int, type_budget: str = None):
    conn = get_db()
    sql = "SELECT code, type_budget, libelle, libelle_abrege FROM mission WHERE annee = ?"
    params = [annee]
    if type_budget:
        sql += " AND type_budget = ?"
        params.append(type_budget)
    sql += " ORDER BY code"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/api/programmes/{annee}")
async def api_programmes(annee: int, mission_code: str = None, ministere_code: int = None):
    conn = get_db()
    sql = """SELECT p.code, p.libelle, p.libelle_abrege, p.mission_code, p.ministere_code,
                    p.type_budget, m.libelle as mission_libelle
             FROM programme p
             LEFT JOIN mission m ON m.annee = p.annee AND m.code = p.mission_code
             WHERE p.annee = ?"""
    params = [annee]
    if mission_code:
        sql += " AND p.mission_code = ?"
        params.append(mission_code)
    if ministere_code:
        sql += " AND p.ministere_code = ?"
        params.append(ministere_code)
    sql += " ORDER BY p.code"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/api/actions/{annee}/{programme_code}")
async def api_actions(annee: int, programme_code: int):
    conn = get_db()
    rows = conn.execute(
        "SELECT code, libelle FROM action WHERE annee = ? AND programme_code = ? ORDER BY code",
        (annee, programme_code)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/api/sous-actions/{annee}/{programme_code}/{action_code}")
async def api_sous_actions(annee: int, programme_code: int, action_code: str):
    conn = get_db()
    rows = conn.execute(
        "SELECT code, libelle FROM sous_action "
        "WHERE annee = ? AND programme_code = ? AND action_code = ? ORDER BY code",
        (annee, programme_code, action_code)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/api/ministeres/{annee}")
async def api_ministeres(annee: int):
    conn = get_db()
    rows = conn.execute(
        "SELECT code, libelle, libelle_abrege FROM ministere WHERE annee = ? ORDER BY code",
        (annee,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── API: titres & categories ───────────────────────────

@app.get("/api/titres")
async def api_titres():
    conn = get_db()
    rows = conn.execute("SELECT code, libelle FROM titre ORDER BY code").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/api/categories")
async def api_categories(titre_code: int = None):
    conn = get_db()
    sql = "SELECT code, titre_code, libelle FROM categorie"
    params = []
    if titre_code:
        sql += " WHERE titre_code = ?"
        params.append(titre_code)
    sql += " ORDER BY code"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── API: budget data ──────────────────────────────────

@app.get("/api/budget/par-mission/{annee}")
async def api_budget_par_mission(annee: int):
    """AE/CP aggregated by mission."""
    conn = get_db()
    rows = conn.execute("""
        SELECT d.mission_code, m.libelle as mission_libelle, m.type_budget,
               SUM(d.ae) as total_ae, SUM(d.cp) as total_cp,
               COUNT(DISTINCT d.programme_code) as nb_programmes
        FROM donnees_budget d
        LEFT JOIN mission m ON m.annee = d.annee AND m.code = d.mission_code
        WHERE d.annee = ?
        GROUP BY d.mission_code
        ORDER BY total_cp DESC
    """, (annee,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/api/budget/par-programme/{annee}")
async def api_budget_par_programme(annee: int, mission_code: str = None):
    """AE/CP aggregated by programme."""
    conn = get_db()
    sql = """
        SELECT d.programme_code, p.libelle as programme_libelle,
               d.mission_code, p.ministere_code,
               SUM(d.ae) as total_ae, SUM(d.cp) as total_cp
        FROM donnees_budget d
        LEFT JOIN programme p ON p.annee = d.annee AND p.code = d.programme_code
        WHERE d.annee = ?
    """
    params = [annee]
    if mission_code:
        sql += " AND d.mission_code = ?"
        params.append(mission_code)
    sql += " GROUP BY d.programme_code ORDER BY total_cp DESC"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/api/budget/par-titre/{annee}")
async def api_budget_par_titre(annee: int):
    """AE/CP aggregated by titre."""
    conn = get_db()
    rows = conn.execute("""
        SELECT d.titre_code, t.libelle as titre_libelle,
               SUM(d.ae) as total_ae, SUM(d.cp) as total_cp
        FROM donnees_budget d
        LEFT JOIN titre t ON t.code = d.titre_code
        WHERE d.annee = ?
        GROUP BY d.titre_code
        ORDER BY d.titre_code
    """, (annee,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── API: full tree for a mission ───────────────────────

@app.get("/api/arbre/{annee}/{mission_code}")
async def api_arbre(annee: int, mission_code: str):
    """Full tree: mission -> programmes -> actions -> sous-actions."""
    conn = get_db()

    mission = conn.execute(
        "SELECT code, libelle, type_budget FROM mission WHERE annee = ? AND code = ?",
        (annee, mission_code)
    ).fetchone()
    if not mission:
        conn.close()
        return {"error": "Mission not found"}

    tree = dict(mission)
    tree["programmes"] = []

    programmes = conn.execute(
        "SELECT code, libelle, ministere_code FROM programme "
        "WHERE annee = ? AND mission_code = ? ORDER BY code",
        (annee, mission_code)
    ).fetchall()

    for pgm in programmes:
        pgm_dict = dict(pgm)
        pgm_dict["actions"] = []

        actions = conn.execute(
            "SELECT code, libelle FROM action "
            "WHERE annee = ? AND programme_code = ? ORDER BY code",
            (annee, pgm["code"])
        ).fetchall()

        for act in actions:
            act_dict = dict(act)
            sous_actions = conn.execute(
                "SELECT code, libelle FROM sous_action "
                "WHERE annee = ? AND programme_code = ? AND action_code = ? ORDER BY code",
                (annee, pgm["code"], act["code"])
            ).fetchall()
            act_dict["sous_actions"] = [dict(sa) for sa in sous_actions]
            pgm_dict["actions"].append(act_dict)

        tree["programmes"].append(pgm_dict)

    conn.close()
    return tree


# ── Static file mounts (must be after all routes) ────
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

RESSOURCES_DIR = PROJECT_ROOT / "ressources"
if RESSOURCES_DIR.exists():
    app.mount("/ressources", StaticFiles(directory=str(RESSOURCES_DIR)), name="ressources")
if Path(ENTRANTS_DIR).exists():
    app.mount("/entrants", StaticFiles(directory=str(ENTRANTS_DIR)), name="entrants")
