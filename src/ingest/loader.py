"""Configuration-driven CSV loader for budget data."""

import csv
import math
import sqlite3
from fnmatch import fnmatch
from pathlib import Path
from typing import Any

import yaml


def load_schema_config(config_path: str) -> dict:
    """Load a YAML schema mapping configuration."""
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def find_source_file(config: dict, data_dir: str) -> Path:
    """Find the source CSV file matching the config's file_pattern."""
    pattern = config["file_pattern"]
    annee = config["derived"]["annee"]
    pattern = pattern.replace("{annee}", str(annee))
    data_path = Path(data_dir)
    matches = [f for f in data_path.iterdir() if f.is_file() and fnmatch(f.name, pattern)]
    if not matches:
        raise FileNotFoundError(f"No file matching '{pattern}' in {data_dir}")
    if len(matches) > 1:
        raise FileNotFoundError(f"Multiple files matching '{pattern}': {matches}")
    return matches[0]


def convert_value(raw: str, col_config: dict) -> Any:
    """Convert a raw CSV string value according to the column config."""
    if raw is None or raw.strip() == "":
        return None
    raw = raw.strip()
    col_type = col_config.get("type", "string")
    if col_type == "string":
        mapping = col_config.get("mapping")
        if mapping:
            return mapping.get(raw, raw)
        return raw
    elif col_type == "integer":
        return int(raw)
    elif col_type == "float":
        return float(raw)
    elif col_type == "float_to_int":
        val = float(raw)
        if math.isnan(val):
            return None
        return int(val)
    elif col_type == "space_int":
        # Handle numbers with spaces as thousands separator (e.g., "460 459")
        cleaned = raw.replace(" ", "").replace("\u00a0", "")
        if not cleaned:
            return None
        return int(cleaned)
    elif col_type == "space_float":
        cleaned = raw.replace(" ", "").replace("\u00a0", "")
        if not cleaned:
            return None
        return float(cleaned)
    return raw


def read_csv(file_path: Path, config: dict) -> list[dict]:
    """Read a CSV and apply the schema mapping, returning normalized rows."""
    source_cfg = config["source"]
    encoding = source_cfg.get("encoding", "utf-8-sig")
    separator = source_cfg.get("separator", ";")
    columns = config["columns"]
    derived = config.get("derived", {})

    rows = []
    with open(file_path, encoding=encoding, newline="") as f:
        reader = csv.DictReader(f, delimiter=separator)
        for raw_row in reader:
            row = {}
            for internal_name, col_cfg in columns.items():
                if col_cfg is None:
                    row[internal_name] = None
                    continue
                source_col = col_cfg["source"]
                raw_val = raw_row.get(source_col)
                nullable = col_cfg.get("nullable", False)
                if raw_val is None or raw_val.strip() == "":
                    row[internal_name] = None
                    if not nullable and col_cfg.get("type") not in (None,):
                        pass  # validation handled later
                else:
                    row[internal_name] = convert_value(raw_val, col_cfg)
            # Skip empty rows (trailing separators in CSV)
            if not row.get("type_budget") and not row.get("programme_code"):
                continue
            for key, val in derived.items():
                row[key] = val
            rows.append(row)
    return rows


def validate_rows(rows: list[dict], config: dict) -> list[str]:
    """Validate loaded rows against the config rules. Returns list of errors."""
    errors = []
    validation = config.get("validation", {})
    valid_types = set(validation.get("type_budget_values", []))

    for i, row in enumerate(rows):
        if valid_types and row.get("type_budget") and row["type_budget"] not in valid_types:
            errors.append(f"Row {i}: invalid type_budget '{row['type_budget']}'")
    return errors


def insert_budget_data(conn: sqlite3.Connection, rows: list[dict], source_file: str):
    """Insert normalized rows into donnees_budget."""
    sql = """
    INSERT INTO donnees_budget (
        annee, exercice, type_budget, mission_code, programme_code,
        action_code, sous_action_code, categorie_code, titre_code,
        ae, cp, ae_fdc_adp, cp_fdc_adp, ministere_nom, ministere_code, source_file
    ) VALUES (
        :annee, :exercice, :type_budget, :mission_code, :programme_code,
        :action_code, :sous_action_code, :categorie_code, :titre_code,
        :ae, :cp, :ae_fdc_adp, :cp_fdc_adp, :ministere_nom, :ministere_code, :source_file
    )
    """
    for row in rows:
        row["source_file"] = source_file
        # Map internal names to DB columns
        params = {
            "annee": row.get("annee"),
            "exercice": row.get("exercice"),
            "type_budget": row.get("type_budget"),
            "mission_code": row.get("mission_code"),
            "programme_code": row.get("programme_code"),
            "action_code": row.get("action_code"),
            "sous_action_code": row.get("sous_action_code"),
            "categorie_code": row.get("categorie_code"),
            "titre_code": row.get("titre_code"),
            "ae": row.get("ae"),
            "cp": row.get("cp"),
            "ae_fdc_adp": row.get("ae_fdc_adp"),
            "cp_fdc_adp": row.get("cp_fdc_adp"),
            "ministere_nom": row.get("ministere_nom"),
            "ministere_code": row.get("ministere_code"),
            "source_file": source_file,
        }
        conn.execute(sql, params)
    conn.commit()


def insert_nomenclature_data(conn: sqlite3.Connection, rows: list[dict], source_file: str):
    """Insert nomenclature-only data (2014-style file with no amounts)."""
    sql = """
    INSERT INTO donnees_budget (
        annee, exercice, type_budget, mission_code, programme_code,
        action_code, sous_action_code, source_file
    ) VALUES (
        :annee, :exercice, :type_budget, :mission_code, :programme_code,
        :action_code, :sous_action_code, :source_file
    )
    """
    for row in rows:
        params = {
            "annee": row.get("annee"),
            "exercice": row.get("exercice"),
            "type_budget": row.get("type_budget"),
            "mission_code": row.get("mission_code"),
            "programme_code": row.get("programme_code"),
            "action_code": row.get("action_code"),
            "sous_action_code": row.get("sous_action_code"),
            "source_file": source_file,
        }
        conn.execute(sql, params)
    conn.commit()


def load_data(conn: sqlite3.Connection, config_path: str, data_dir: str) -> dict:
    """Main entry point: load a CSV into the database using a YAML config.

    Returns a summary dict with counts and any errors.
    """
    config = load_schema_config(config_path)
    source_file = find_source_file(config, data_dir)
    rows = read_csv(source_file, config)
    errors = validate_rows(rows, config)

    if errors:
        return {"status": "error", "file": str(source_file), "rows": 0, "errors": errors}

    has_amounts = any(row.get("ae") is not None for row in rows)
    if has_amounts:
        insert_budget_data(conn, rows, str(source_file.name))
    else:
        insert_nomenclature_data(conn, rows, str(source_file.name))

    # Log the load
    conn.execute(
        "INSERT INTO load_log (operation, annee, exercice, source_file, rows_loaded, status) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        ("load_data", config["derived"]["annee"], config["derived"]["exercice"],
         str(source_file.name), len(rows), "success"),
    )
    conn.commit()

    return {"status": "success", "file": str(source_file.name), "rows": len(rows), "errors": []}
