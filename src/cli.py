"""CLI entry point for the budget classification system."""

import argparse
import json
import sys
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = str(PROJECT_ROOT / "db" / "budget.db")
CONFIG_DIR = str(PROJECT_ROOT / "config")
# Use ressources/data if it exists (git-tracked), fallback to entrants/
_ressources_data = PROJECT_ROOT / "ressources" / "data"
_entrants_data = PROJECT_ROOT / "entrants" / "plf open data"
DATA_DIR = str(_ressources_data if _ressources_data.exists() else _entrants_data)
ENTRANTS_DIR = str(PROJECT_ROOT / "entrants")

sys.path.insert(0, str(PROJECT_ROOT))

from src.models.schema import init_db, get_connection
from src.ingest.loader import load_schema_config, find_source_file, read_csv, load_data
from src.ingest.nomenclature import load_constants, enrich_nomenclature_from_csv, load_nomenclature_xls_format
from src.ingest.documents import load_documents
from src.ingest.reconciliation import build_canonical_entities
from src.validate.checks import run_all_checks


def cmd_init(args):
    """Initialize the database and load constants."""
    print(f"Initializing database at {DB_PATH}...")
    conn = init_db(DB_PATH)
    constants_path = Path(CONFIG_DIR) / "constants.yaml"
    load_constants(conn, str(constants_path))
    conn.close()
    print("Database initialized with constants.")


def cmd_load(args):
    """Load data from a CSV using a schema config."""
    annee = args.year
    config_name = f"opendata_{annee}.yaml"
    config_path = str(Path(CONFIG_DIR) / "schemas" / config_name)

    if not Path(config_path).exists():
        print(f"ERROR: Config not found: {config_path}")
        sys.exit(1)

    conn = get_connection(DB_PATH)

    # Clear existing data for this year+exercice to allow re-loads
    config = load_schema_config(config_path)
    exercice = config["derived"]["exercice"]
    conn.execute(
        "DELETE FROM donnees_budget WHERE annee = ? AND exercice = ?",
        (annee, exercice),
    )

    # Load data
    print(f"Loading data for {exercice} {annee}...")
    result = load_data(conn, config_path, DATA_DIR)
    print(f"  File: {result['file']}")
    print(f"  Rows: {result['rows']}")
    if result["errors"]:
        print(f"  ERRORS: {len(result['errors'])}")
        for e in result["errors"][:10]:
            print(f"    - {e}")

    # Enrich nomenclature from the same CSV
    if result["status"] == "success":
        print(f"Building nomenclature for {annee}...")
        source_file = find_source_file(config, DATA_DIR)
        rows = read_csv(source_file, config)
        nom_stats = enrich_nomenclature_from_csv(conn, rows, annee)
        print(f"  Missions: {nom_stats['missions']}")
        print(f"  Programmes: {nom_stats['programmes']}")
        print(f"  Actions: {nom_stats['actions']}")
        print(f"  Sous-actions: {nom_stats['sous_actions']}")

    conn.close()
    print("Done.")


def cmd_load_documents(args):
    """Load document metadata from PDF scan."""
    annee = args.year
    config_name = f"plf_{annee}.yaml"
    config_path = str(Path(CONFIG_DIR) / "documents" / config_name)

    if not Path(config_path).exists():
        print(f"ERROR: Config not found: {config_path}")
        sys.exit(1)

    conn = get_connection(DB_PATH)

    # Clear existing documents for this year
    conn.execute("DELETE FROM document WHERE annee = ?", (annee,))

    print(f"Scanning documents for PLF {annee}...")
    result = load_documents(conn, config_path, ENTRANTS_DIR)
    print(f"  Total PDFs found: {result.get('total_pdfs', 0)}")
    print(f"  Successfully parsed: {result.get('parsed', 0)}")
    print(f"    MSN (mission): {result.get('by_level', {}).get('MSN', 0)}")
    print(f"    PGM (programme): {result.get('by_level', {}).get('PGM', 0)}")
    if result.get("unparsed"):
        print(f"  Unparsed files ({len(result['unparsed'])}):")
        for f in result["unparsed"][:10]:
            print(f"    - {f}")

    conn.close()
    print("Done.")


def cmd_load_nomenclature(args):
    """Load a nomenclature file in XLS-like format (TTR/CAT/MIN/MSN/PGM/ACT/SSA)."""
    annee = args.year
    config_name = f"nomenclature_{annee}.yaml"
    config_path = str(Path(CONFIG_DIR) / "schemas" / config_name)

    if not Path(config_path).exists():
        print(f"ERROR: Config not found: {config_path}")
        sys.exit(1)

    conn = get_connection(DB_PATH)

    # Clear existing nomenclature for this year
    for table in ("sous_action", "action", "programme", "mission", "ministere"):
        conn.execute(f"DELETE FROM {table} WHERE annee = ?", (annee,))

    print(f"Loading nomenclature for {annee}...")
    result = load_nomenclature_xls_format(conn, config_path, DATA_DIR)
    if result["status"] == "error":
        print(f"  ERROR: {result['message']}")
        sys.exit(1)
    print(f"  File: {result['file']}")
    print(f"  Ministères: {result['ministeres']}")
    print(f"  Missions: {result['missions']}")
    print(f"  Programmes: {result['programmes']}")
    print(f"  Actions: {result['actions']}")
    print(f"  Sous-actions: {result['sous_actions']}")

    conn.close()
    print("Done.")


def cmd_reconcile(args):
    """Build canonical entities from reconciliation config."""
    config_path = str(Path(CONFIG_DIR) / "reconciliation" / "programmes.yaml")

    if not Path(config_path).exists():
        print(f"ERROR: Config not found: {config_path}")
        sys.exit(1)

    conn = get_connection(DB_PATH)
    print("Building canonical entities...")
    result = build_canonical_entities(conn, config_path)
    print(f"  Canonical entities created: {result['canonical_created']}")
    print(f"  Year mappings created: {result['mappings_created']}")
    print(f"  Events recorded: {result['events_created']}")
    if result["unmatched_programmes"]:
        print(f"  Unmatched programmes ({len(result['unmatched_programmes'])}):")
        for annee, code, libelle in result["unmatched_programmes"][:20]:
            print(f"    - {annee}: {code} ({libelle})")

    conn.close()
    print("Done.")


def cmd_validate(args):
    """Run validation checks."""
    annee = args.year
    conn = get_connection(DB_PATH)
    print(f"Validating data for {annee}...")
    report = run_all_checks(conn, annee)

    # Stats
    stats = report["stats"]
    print(f"\n  === Stats {annee} ===")
    print(f"  Data rows:      {stats['data_rows']}")
    print(f"  Programmes:     {stats['programmes_in_data']} (data) / {stats['programmes_in_nomenclature']} (nomenclature)")
    print(f"  Missions:       {stats['missions']}")
    print(f"  Actions:        {stats['actions']}")
    print(f"  Documents:      {stats['documents']}")
    if stats.get("total_ae"):
        print(f"  Total AE:       {stats['total_ae']:,.0f}")
        print(f"  Total CP:       {stats['total_cp']:,.0f}")

    # Errors
    if report["referential_integrity"]:
        print(f"\n  === Referential Integrity ERRORS ({len(report['referential_integrity'])}) ===")
        for e in report["referential_integrity"][:10]:
            print(f"    {e}")

    if report["document_coverage"]:
        print(f"\n  === Document Coverage ERRORS ({len(report['document_coverage'])}) ===")
        for e in report["document_coverage"][:10]:
            print(f"    {e}")

    if report["completeness"]:
        print(f"\n  === Completeness WARNINGS ({len(report['completeness'])}) ===")
        for w in report["completeness"][:10]:
            print(f"    {w}")

    # Summary
    s = report["summary"]
    print(f"\n  === Summary: {s['status']} ({s['errors']} errors, {s['warnings']} warnings) ===")

    conn.close()


def cmd_load_all(args):
    """Load everything for a given year."""
    # Init if needed
    if not Path(DB_PATH).exists():
        cmd_init(args)

    # Try opendata CSV first, then nomenclature format
    opendata_config = Path(CONFIG_DIR) / "schemas" / f"opendata_{args.year}.yaml"
    nomenclature_config = Path(CONFIG_DIR) / "schemas" / f"nomenclature_{args.year}.yaml"

    if opendata_config.exists():
        cmd_load(args)
    elif nomenclature_config.exists():
        cmd_load_nomenclature(args)
    else:
        print(f"ERROR: No config found for {args.year} (tried opendata_{args.year}.yaml and nomenclature_{args.year}.yaml)")
        sys.exit(1)

    # Try to load documents if config exists
    doc_config = Path(CONFIG_DIR) / "documents" / f"plf_{args.year}.yaml"
    if doc_config.exists():
        cmd_load_documents(args)

    cmd_validate(args)


def main():
    parser = argparse.ArgumentParser(description="Budget classification system")
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # init
    sub.add_parser("init", help="Initialize database and load constants")

    # load
    p_load = sub.add_parser("load", help="Load CSV data for a year")
    p_load.add_argument("year", type=int, help="Budget year (e.g. 2025)")

    # load-documents
    p_docs = sub.add_parser("load-documents", help="Scan and load PDF documents")
    p_docs.add_argument("year", type=int, help="Budget year")

    # load-nomenclature
    p_nom = sub.add_parser("load-nomenclature", help="Load nomenclature file (XLS format)")
    p_nom.add_argument("year", type=int, help="Budget year")

    # reconcile
    sub.add_parser("reconcile", help="Build canonical entities")

    # validate
    p_val = sub.add_parser("validate", help="Run validation checks")
    p_val.add_argument("year", type=int, help="Budget year")

    # load-all
    p_all = sub.add_parser("load-all", help="Load data + documents + validate")
    p_all.add_argument("year", type=int, help="Budget year")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "init": cmd_init,
        "load": cmd_load,
        "load-nomenclature": cmd_load_nomenclature,
        "load-documents": cmd_load_documents,
        "reconcile": cmd_reconcile,
        "validate": cmd_validate,
        "load-all": cmd_load_all,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
