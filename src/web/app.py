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


@app.get("/prototypes")
async def prototypes():
    return FileResponse(STATIC_DIR / "prototypes.html")


@app.get("/analyse-existant")
async def analyse_existant():
    return FileResponse(STATIC_DIR / "analyse-existant.html")


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


# ── API: budget by ministere ──────────────────────────

@app.get("/api/budget/par-ministere/{annee}")
async def api_budget_par_ministere(annee: int):
    """AE/CP aggregated by ministere_nom."""
    conn = get_db()
    rows = conn.execute("""
        SELECT ministere_nom,
               COUNT(DISTINCT programme_code) as nb_programmes,
               COUNT(DISTINCT mission_code) as nb_missions,
               SUM(ae) as total_ae, SUM(cp) as total_cp
        FROM donnees_budget
        WHERE annee = ? AND ministere_nom IS NOT NULL
        GROUP BY ministere_nom
        ORDER BY total_cp DESC
    """, (annee,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/api/budget/hierarchie/{annee}")
async def api_budget_hierarchie(annee: int):
    """Full hierarchy: ministere -> mission -> programme with AE/CP."""
    conn = get_db()
    rows = conn.execute("""
        SELECT d.ministere_nom, d.mission_code, m.libelle as mission_libelle,
               m.type_budget, d.programme_code, p.libelle as programme_libelle,
               SUM(d.ae) as total_ae, SUM(d.cp) as total_cp
        FROM donnees_budget d
        LEFT JOIN mission m ON m.annee = d.annee AND m.code = d.mission_code
        LEFT JOIN programme p ON p.annee = d.annee AND p.code = d.programme_code
        WHERE d.annee = ?
        GROUP BY d.ministere_nom, d.mission_code, d.programme_code
        ORDER BY total_cp DESC
    """, (annee,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/api/documents/{annee}")
async def api_documents(annee: int, programme_code: int = None, mission_code: str = None):
    """List documents (PAP PDFs) for a given year."""
    conn = get_db()
    sql = "SELECT * FROM document WHERE annee = ?"
    params: list = [annee]
    if programme_code is not None:
        sql += " AND programme_code = ?"
        params.append(programme_code)
    if mission_code is not None:
        sql += " AND mission_code = ?"
        params.append(mission_code)
    sql += " ORDER BY type_budget, niveau, programme_code"
    rows = conn.execute(sql, params).fetchall()
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


# ── API: corpus (document tree for a year+exercice) ──

@app.get("/api/corpus/{annee}")
async def api_corpus(annee: int, exercice: str = None):
    """Build the corpus tree for the corpus page: documents grouped by type_budget > mission > programme."""
    conn = get_db()

    # If no exercice specified, pick the first available for this year
    if not exercice:
        row = conn.execute(
            "SELECT DISTINCT exercice FROM document WHERE annee = ? ORDER BY exercice", (annee,)
        ).fetchone()
        exercice = row["exercice"] if row else "PLF"

    docs = conn.execute(
        "SELECT * FROM document WHERE annee = ? AND exercice = ? ORDER BY type_budget, niveau, mission_code, programme_code",
        (annee, exercice)
    ).fetchall()

    # Build the tree structure expected by corpus.html
    tree = {}
    for doc in docs:
        d = dict(doc)
        tb = d["type_budget"]
        mc = d["mission_code"] or tb  # CCO/COM have no mission_code
        if tb not in tree:
            tree[tb] = {"missions": {}}

        if mc not in tree[tb]["missions"]:
            # Get mission name from nomenclature
            msn = conn.execute(
                "SELECT libelle FROM mission WHERE annee = ? AND code = ?", (annee, mc)
            ).fetchone()
            tree[tb]["missions"][mc] = {
                "name": msn["libelle"] if msn else mc,
                "programmes": [],
                "msn_path": None
            }

        if d["niveau"] == "MSN":
            tree[tb]["missions"][mc]["msn_path"] = d["filepath"]
        elif d["niveau"] == "PGM" and d["programme_code"]:
            # Get programme name from nomenclature
            pgm = conn.execute(
                "SELECT libelle FROM programme WHERE annee = ? AND code = ?",
                (annee, d["programme_code"])
            ).fetchone()
            tree[tb]["missions"][mc]["programmes"].append({
                "num": str(d["programme_code"]),
                "name": pgm["libelle"] if pgm else "",
                "path": d["filepath"]
            })

    conn.close()

    # Determine the file base path
    exercice_dir = "PLRG" if exercice == "PLR" else "PLF"
    file_base = f"/ressources/docs/{annee}/{exercice_dir}/"

    # Available exercices for this year
    conn2 = get_db()
    exercices = [r["exercice"] for r in conn2.execute(
        "SELECT DISTINCT exercice FROM document WHERE annee = ? ORDER BY exercice", (annee,)
    ).fetchall()]
    conn2.close()

    return {
        "annee": annee,
        "exercice": exercice,
        "exercice_dir": exercice_dir,
        "file_base": file_base,
        "exercices_disponibles": exercices,
        "tree": tree
    }


# ── Static file mounts (must be after all routes) ────
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

RESSOURCES_DIR = PROJECT_ROOT / "ressources"
if RESSOURCES_DIR.exists():
    app.mount("/ressources", StaticFiles(directory=str(RESSOURCES_DIR)), name="ressources")
if Path(ENTRANTS_DIR).exists():
    app.mount("/entrants", StaticFiles(directory=str(ENTRANTS_DIR)), name="entrants")
