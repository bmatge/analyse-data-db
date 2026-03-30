"""PDF document scanner and linker."""

import re
import sqlite3
from pathlib import Path

import yaml


def load_document_config(config_path: str) -> dict:
    """Load a YAML document pattern configuration."""
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def scan_pdfs(root_path: Path) -> list[Path]:
    """Recursively find all PDF files under root_path."""
    return sorted(root_path.rglob("*.pdf"))


def parse_mission_pdf(filepath: Path, root: Path, config: dict) -> dict | None:
    """Parse a mission-level PDF filename and path.

    Expected paths:
      PLF: {root}/{type_budget}/MSN/{mission_code}/PAP2025_BG_Name_XX.pdf
      PLR: {root}/{type_budget}/MSN/{mission_code}/FR_2023_PLR_BG_MSN_XX.pdf
    """
    rel = filepath.relative_to(root)
    parts = rel.parts

    if len(parts) < 4 or parts[1] != "MSN":
        return None

    type_budget = parts[0]
    mission_code = parts[2]
    filename = parts[3]

    # PLF format: PAP2025_BG_Name_XX.pdf
    match = re.match(r"PAP\d{4}_(.+?)_(.+?)_([A-Z]{2})\.pdf", filename)
    if match:
        return {
            "annee": config["annee"],
            "exercice": config["exercice"],
            "type_document": config["type_document"],
            "type_budget": type_budget,
            "niveau": "MSN",
            "mission_code": match.group(3),
            "programme_code": None,
            "filename": filename,
            "filepath": str(rel),
            "titre": match.group(2).replace("_", " "),
        }

    # PLR format: FR_2023_PLR_BG_MSN_XX.pdf
    match = re.match(r"FR_(\d{4})_PLR_([A-Z]+)_MSN_([A-Z]{2})\.pdf", filename)
    if match:
        return {
            "annee": config["annee"],
            "exercice": config["exercice"],
            "type_document": config["type_document"],
            "type_budget": type_budget,
            "niveau": "MSN",
            "mission_code": match.group(3),
            "programme_code": None,
            "filename": filename,
            "filepath": str(rel),
            "titre": None,
        }

    return None


def parse_programme_pdf(filepath: Path, root: Path, config: dict) -> dict | None:
    """Parse a programme-level PDF filename and path.

    Expected path: {root}/{type_budget}/PGM/{programme_code}/FR_2025_PLF_XX_PGM_NNN.pdf
    """
    rel = filepath.relative_to(root)
    parts = rel.parts

    if len(parts) < 4 or parts[1] != "PGM":
        return None

    type_budget = parts[0]
    programme_code_dir = parts[2]
    filename = parts[3]

    # PLF format: FR_2025_PLF_XX_PGM_NNN.pdf
    match = re.match(r"FR_(\d{4})_PLF_([A-Z]{2})_PGM_(\d{3})\.pdf", filename)
    if match:
        return {
            "annee": config["annee"],
            "exercice": config["exercice"],
            "type_document": config["type_document"],
            "type_budget": type_budget,
            "niveau": "PGM",
            "mission_code": match.group(2),
            "programme_code": int(match.group(3)),
            "filename": filename,
            "filepath": str(rel),
            "titre": None,
        }

    # PLR format: FR_2023_PLR_XX_PGM_NNN.pdf
    match = re.match(r"FR_(\d{4})_PLR_([A-Z]{2})_PGM_(\d{3})\.pdf", filename)
    if match:
        return {
            "annee": config["annee"],
            "exercice": config["exercice"],
            "type_document": config["type_document"],
            "type_budget": type_budget,
            "niveau": "PGM",
            "mission_code": match.group(2),
            "programme_code": int(match.group(3)),
            "filename": filename,
            "filepath": str(rel),
            "titre": None,
        }

    return None


def parse_special_pdf(filepath: Path, root: Path, config: dict) -> dict | None:
    """Parse a special PDF (CCO, COM) using the config's special patterns."""
    rel = filepath.relative_to(root)
    specials = config.get("patterns", {}).get("special", [])

    for spec in specials:
        if filepath.name == spec["filename"]:
            return {
                "annee": config["annee"],
                "exercice": config["exercice"],
                "type_document": config["type_document"],
                "type_budget": spec["type_budget"],
                "niveau": "MSN",
                "mission_code": spec.get("mission_code"),
                "programme_code": spec.get("programme_code"),
                "filename": filepath.name,
                "filepath": str(rel),
                "titre": filepath.stem.split("_", 3)[-1].replace("_", " ") if "_" in filepath.stem else None,
            }
    return None


def parse_pdf(filepath: Path, root: Path, config: dict) -> dict | None:
    """Try all parsers on a PDF file."""
    result = parse_mission_pdf(filepath, root, config)
    if result:
        return result
    result = parse_programme_pdf(filepath, root, config)
    if result:
        return result
    result = parse_special_pdf(filepath, root, config)
    if result:
        return result
    return None


def enrich_nomenclature_from_documents(conn: sqlite3.Connection, docs: list[dict], annee: int):
    """Add missions and programmes found in documents but missing from the CSV nomenclature.

    This handles CAS/CCF programmes that appear in PDFs but not in the open data CSV
    (which may only cover BG+BA).
    """
    for doc in docs:
        mc = doc.get("mission_code")
        tb = doc.get("type_budget")
        pc = doc.get("programme_code")

        if mc and tb:
            conn.execute(
                "INSERT OR IGNORE INTO mission (annee, code, type_budget, libelle) "
                "VALUES (?, ?, ?, '')",
                (annee, mc, tb),
            )

        if pc is not None and tb:
            conn.execute(
                "INSERT OR IGNORE INTO programme (annee, code, libelle, mission_code, type_budget) "
                "VALUES (?, ?, '', ?, ?)",
                (annee, int(pc), mc or "", tb),
            )

    conn.commit()


def insert_documents(conn: sqlite3.Connection, docs: list[dict]):
    """Insert parsed document records into the database."""
    sql = """
    INSERT OR IGNORE INTO document (
        annee, exercice, type_document, type_budget, niveau,
        mission_code, programme_code, filename, filepath, titre
    ) VALUES (
        :annee, :exercice, :type_document, :type_budget, :niveau,
        :mission_code, :programme_code, :filename, :filepath, :titre
    )
    """
    for doc in docs:
        conn.execute(sql, doc)
    conn.commit()


def load_documents(conn: sqlite3.Connection, config_path: str, base_dir: str) -> dict:
    """Main entry point: scan PDFs and load them into the database.

    Returns a summary dict.
    """
    config = load_document_config(config_path)
    # Try ressources/docs first (git-tracked, first-page PDFs), then entrants/
    project_root = Path(base_dir).parent if Path(base_dir).name == "entrants" else Path(base_dir).parent
    ressources_root = project_root / "ressources" / "docs" / config["root_path"]
    entrants_root = Path(base_dir) / config["root_path"]
    root = ressources_root if ressources_root.exists() else entrants_root

    if not root.exists():
        return {"status": "error", "message": f"Root path not found (tried {ressources_root} and {entrants_root})"}

    pdfs = scan_pdfs(root)
    parsed = []
    unparsed = []

    for pdf in pdfs:
        doc = parse_pdf(pdf, root, config)
        if doc:
            parsed.append(doc)
        else:
            unparsed.append(str(pdf.relative_to(root)))

    insert_documents(conn, parsed)

    # Enrich nomenclature: add missions/programmes found in documents but not in CSV data
    enrich_nomenclature_from_documents(conn, parsed, config["annee"])

    # Log
    conn.execute(
        "INSERT INTO load_log (operation, annee, exercice, rows_loaded, status, message) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        ("load_documents", config["annee"], config["exercice"], len(parsed), "success",
         f"{len(unparsed)} unparsed files"),
    )
    conn.commit()

    return {
        "status": "success",
        "total_pdfs": len(pdfs),
        "parsed": len(parsed),
        "unparsed": unparsed,
        "by_level": {
            "MSN": sum(1 for d in parsed if d["niveau"] == "MSN"),
            "PGM": sum(1 for d in parsed if d["niveau"] == "PGM"),
        },
    }
