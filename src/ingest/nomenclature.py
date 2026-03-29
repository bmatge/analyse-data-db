"""Build nomenclature snapshots from loaded data or XLS files."""

import csv
import sqlite3
from fnmatch import fnmatch
from pathlib import Path

import yaml


def load_constants(conn: sqlite3.Connection, constants_path: str):
    """Load invariant constants (type_budget, titres, categories) into the database."""
    with open(constants_path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    # Type budget
    for code, libelle in cfg["type_budget"].items():
        conn.execute(
            "INSERT OR IGNORE INTO type_budget (code, libelle) VALUES (?, ?)",
            (code, libelle),
        )

    # Titres
    for code, libelle in cfg["titres"].items():
        conn.execute(
            "INSERT OR IGNORE INTO titre (code, libelle) VALUES (?, ?)",
            (int(code), libelle),
        )

    # Categories
    for code, info in cfg["categories"].items():
        conn.execute(
            "INSERT OR IGNORE INTO categorie (code, titre_code, libelle) VALUES (?, ?, ?)",
            (int(code), info["titre"], info["libelle"]),
        )

    conn.commit()


def load_nomenclature_xls_format(conn: sqlite3.Connection, config_path: str, data_dir: str) -> dict:
    """Load a nomenclature file in XLS-like format (TTR/CAT/MIN/MSN/PGM/ACT/SSA rows).

    This handles files like PLF_2022_Nomenclature.csv that have the same structure
    as the Nomenclature XLS: Type ligne, Type Budget, code, Mission, Ministere, Libelle, etc.
    """
    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    annee = config["derived"]["annee"]
    source_cfg = config["source"]
    encoding = source_cfg.get("encoding", "utf-8-sig")
    separator = source_cfg.get("separator", ";")
    pattern = config["file_pattern"]
    cols = config["columns"]

    # Find the file
    data_path = Path(data_dir)
    matches = [f for f in data_path.iterdir() if f.is_file() and fnmatch(f.name, pattern)]
    if not matches:
        return {"status": "error", "message": f"No file matching '{pattern}' in {data_dir}"}
    source_file = matches[0]

    stats = {"ministeres": 0, "missions": 0, "programmes": 0, "actions": 0, "sous_actions": 0}

    with open(source_file, encoding=encoding, newline="") as f:
        reader = csv.DictReader(f, delimiter=separator)
        for raw_row in reader:
            type_ligne = (raw_row.get(cols["type_ligne"]["source"]) or "").strip()
            type_budget = (raw_row.get(cols["type_budget"]["source"]) or "").strip()
            code = (raw_row.get(cols["code"]["source"]) or "").strip()
            mission_code = (raw_row.get(cols["mission"]["source"]) or "").strip()
            ministere_code = (raw_row.get(cols["ministere"]["source"]) or "").strip()
            libelle = (raw_row.get(cols["libelle"]["source"]) or "").strip()
            libelle_abrege = (raw_row.get(cols["libelle_abrege"]["source"]) or "").strip()
            commentaire = (raw_row.get(cols["commentaire"]["source"]) or "").strip()

            if type_ligne == "MIN" and code:
                conn.execute(
                    "INSERT OR IGNORE INTO ministere (annee, code, libelle, libelle_abrege) "
                    "VALUES (?, ?, ?, ?)",
                    (annee, int(code), libelle, libelle_abrege),
                )
                stats["ministeres"] += 1

            elif type_ligne == "MSN" and code:
                conn.execute(
                    "INSERT OR IGNORE INTO mission (annee, code, type_budget, libelle, libelle_abrege) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (annee, code, type_budget, libelle, libelle_abrege),
                )
                stats["missions"] += 1

            elif type_ligne == "PGM" and code:
                ministere_int = int(ministere_code) if ministere_code else None
                conn.execute(
                    "INSERT OR IGNORE INTO programme "
                    "(annee, code, libelle, libelle_abrege, mission_code, ministere_code, type_budget, commentaire) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (annee, int(code), libelle, libelle_abrege, mission_code,
                     ministere_int, type_budget, commentaire),
                )
                stats["programmes"] += 1

            elif type_ligne == "ACT" and code:
                # Code format: PGM-NN (e.g., "105-01")
                parts = code.split("-", 1)
                if len(parts) == 2:
                    pgm_code = int(parts[0])
                    act_code = parts[1]
                    conn.execute(
                        "INSERT OR IGNORE INTO action (annee, programme_code, code, libelle) "
                        "VALUES (?, ?, ?, ?)",
                        (annee, pgm_code, act_code, libelle),
                    )
                    stats["actions"] += 1

            elif type_ligne == "SSA" and code:
                # Code format: PGM-NN-NN (e.g., "105-01-01")
                parts = code.split("-", 2)
                if len(parts) == 3:
                    pgm_code = int(parts[0])
                    act_code = parts[1]
                    ssa_code = parts[2]
                    conn.execute(
                        "INSERT OR IGNORE INTO sous_action "
                        "(annee, programme_code, action_code, code, libelle) "
                        "VALUES (?, ?, ?, ?, ?)",
                        (annee, pgm_code, act_code, ssa_code, libelle),
                    )
                    stats["sous_actions"] += 1

    conn.execute(
        "INSERT INTO load_log (operation, annee, exercice, source_file, rows_loaded, status) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        ("load_nomenclature", annee, config["derived"]["exercice"],
         source_file.name, sum(stats.values()), "success"),
    )
    conn.commit()

    return {"status": "success", "file": source_file.name, **stats}


def build_nomenclature_from_data(conn: sqlite3.Connection, annee: int):
    """Extract nomenclature snapshot from donnees_budget for a given year.

    This derives missions, programmes, and actions from the data already loaded.
    """
    # Extract missions
    rows = conn.execute("""
        SELECT DISTINCT type_budget, mission_code, mission_libelle
        FROM (
            SELECT type_budget, mission_code,
                   NULL as mission_libelle
            FROM donnees_budget
            WHERE annee = ? AND mission_code IS NOT NULL
        )
        WHERE mission_code IS NOT NULL
    """, (annee,)).fetchall()

    # For missions, we need the libelle — get it from a join or from a separate source
    # Use a more complete query that gets mission info from the data
    mission_rows = conn.execute("""
        SELECT DISTINCT type_budget, mission_code
        FROM donnees_budget
        WHERE annee = ? AND mission_code IS NOT NULL
    """, (annee,)).fetchall()

    for row in mission_rows:
        conn.execute(
            "INSERT OR IGNORE INTO mission (annee, code, type_budget, libelle) VALUES (?, ?, ?, ?)",
            (annee, row[1], row[0], ""),  # libelle will be updated below
        )

    # Extract programmes (with mission link and libelle)
    pgm_rows = conn.execute("""
        SELECT DISTINCT type_budget, mission_code, programme_code, programme_libelle, ministere_nom
        FROM (
            SELECT d.type_budget, d.mission_code, d.programme_code,
                   '' as programme_libelle, d.ministere_nom
            FROM donnees_budget d
            WHERE d.annee = ?
        )
        WHERE programme_code IS NOT NULL
        GROUP BY programme_code
    """, (annee,)).fetchall()

    for row in pgm_rows:
        conn.execute(
            "INSERT OR IGNORE INTO programme (annee, code, libelle, mission_code, type_budget) "
            "VALUES (?, ?, ?, ?, ?)",
            (annee, row[2], row[3] or "", row[1] or "", row[0]),
        )

    # Extract actions
    act_rows = conn.execute("""
        SELECT DISTINCT programme_code, action_code, '' as action_libelle
        FROM donnees_budget
        WHERE annee = ? AND action_code IS NOT NULL
    """, (annee,)).fetchall()

    for row in act_rows:
        conn.execute(
            "INSERT OR IGNORE INTO action (annee, programme_code, code, libelle) "
            "VALUES (?, ?, ?, ?)",
            (annee, row[0], str(row[1]), row[2] or ""),
        )

    conn.commit()


def build_nomenclature_from_opendata(conn: sqlite3.Connection, annee: int):
    """Build a richer nomenclature from the open data CSV that's been loaded.

    The 2024/2025 format has mission libelle, programme libelle, action libelle,
    ministere name — all derivable from donnees_budget.
    """
    # Missions: get distinct (type_budget, mission_code) with a representative libelle
    # We need to get libelles — they're not in donnees_budget directly.
    # Re-read from the CSV? No — let's query what we have.
    # For now, build from loaded data with empty libelles; the enrichment
    # comes from the CSV re-read in the CLI.
    build_nomenclature_from_data(conn, annee)


def enrich_nomenclature_from_csv(conn: sqlite3.Connection, rows: list[dict], annee: int):
    """Enrich nomenclature tables with libelles from parsed CSV rows.

    Called after load_data with the same parsed rows to fill in labels.
    """
    missions_seen = {}
    programmes_seen = {}
    actions_seen = {}
    sous_actions_seen = {}

    for row in rows:
        # Missions
        mc = row.get("mission_code")
        if mc and mc not in missions_seen:
            missions_seen[mc] = {
                "type_budget": row.get("type_budget"),
                "libelle": row.get("mission_libelle", ""),
            }

        # Programmes
        pc = row.get("programme_code")
        if pc and pc not in programmes_seen:
            programmes_seen[pc] = {
                "type_budget": row.get("type_budget"),
                "mission_code": mc,
                "libelle": row.get("programme_libelle", ""),
                "ministere_nom": row.get("ministere_nom"),
            }

        # Actions
        ac = row.get("action_code")
        if pc and ac:
            key = (pc, str(ac))
            if key not in actions_seen:
                actions_seen[key] = row.get("action_libelle", "")

        # Sous-actions
        sac = row.get("sous_action_code")
        if pc and ac and sac:
            key = (pc, str(ac), str(sac))
            if key not in sous_actions_seen:
                sous_actions_seen[key] = row.get("sous_action_libelle", "")

    # Upsert missions
    for code, info in missions_seen.items():
        conn.execute(
            "INSERT INTO mission (annee, code, type_budget, libelle) "
            "VALUES (?, ?, ?, ?) "
            "ON CONFLICT (annee, code) DO UPDATE SET libelle=excluded.libelle, type_budget=excluded.type_budget",
            (annee, code, info["type_budget"], info["libelle"] or ""),
        )

    # Upsert programmes
    for code, info in programmes_seen.items():
        conn.execute(
            "INSERT INTO programme (annee, code, libelle, mission_code, type_budget) "
            "VALUES (?, ?, ?, ?, ?) "
            "ON CONFLICT (annee, code) DO UPDATE SET "
            "libelle=excluded.libelle, mission_code=excluded.mission_code, type_budget=excluded.type_budget",
            (annee, int(code), info["libelle"] or "", info["mission_code"] or "", info["type_budget"] or ""),
        )

    # Upsert actions
    for (pgm, act), libelle in actions_seen.items():
        conn.execute(
            "INSERT INTO action (annee, programme_code, code, libelle) "
            "VALUES (?, ?, ?, ?) "
            "ON CONFLICT (annee, programme_code, code) DO UPDATE SET libelle=excluded.libelle",
            (annee, int(pgm), act, libelle or ""),
        )

    # Upsert sous-actions
    for (pgm, act, sact), libelle in sous_actions_seen.items():
        conn.execute(
            "INSERT INTO sous_action (annee, programme_code, action_code, code, libelle) "
            "VALUES (?, ?, ?, ?, ?) "
            "ON CONFLICT (annee, programme_code, action_code, code) DO UPDATE SET libelle=excluded.libelle",
            (annee, int(pgm), act, sact, libelle or ""),
        )

    conn.commit()
    return {
        "missions": len(missions_seen),
        "programmes": len(programmes_seen),
        "actions": len(actions_seen),
        "sous_actions": len(sous_actions_seen),
    }
