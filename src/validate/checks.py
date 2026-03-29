"""Post-load validation checks."""

import sqlite3


def check_referential_integrity(conn: sqlite3.Connection, annee: int) -> list[str]:
    """Check that every programme_code in data exists in nomenclature."""
    errors = []
    rows = conn.execute("""
        SELECT DISTINCT d.programme_code
        FROM donnees_budget d
        LEFT JOIN programme p ON d.programme_code = p.code AND d.annee = p.annee
        WHERE d.annee = ? AND p.code IS NULL
    """, (annee,)).fetchall()

    for row in rows:
        errors.append(f"Programme {row[0]} in data but not in nomenclature for {annee}")
    return errors


def check_completeness(conn: sqlite3.Connection, annee: int) -> list[str]:
    """Check that every programme in nomenclature has at least one data row."""
    warnings = []
    rows = conn.execute("""
        SELECT p.code, p.libelle
        FROM programme p
        LEFT JOIN donnees_budget d ON p.code = d.programme_code AND p.annee = d.annee
        WHERE p.annee = ? AND d.programme_code IS NULL
    """, (annee,)).fetchall()

    for row in rows:
        warnings.append(f"Programme {row[0]} ({row[1]}) in nomenclature but no data for {annee}")
    return warnings


def check_document_coverage(conn: sqlite3.Connection, annee: int) -> list[str]:
    """Check that documents map to known programmes/missions."""
    errors = []

    # Check programme-level docs
    rows = conn.execute("""
        SELECT d.programme_code, d.filename
        FROM document d
        LEFT JOIN programme p ON d.programme_code = p.code AND d.annee = p.annee
        WHERE d.annee = ? AND d.niveau = 'PGM' AND d.programme_code IS NOT NULL AND p.code IS NULL
    """, (annee,)).fetchall()

    for row in rows:
        errors.append(f"Document {row[1]} references programme {row[0]} not in nomenclature")

    # Check mission-level docs
    rows = conn.execute("""
        SELECT d.mission_code, d.filename
        FROM document d
        LEFT JOIN mission m ON d.mission_code = m.code AND d.annee = m.annee
        WHERE d.annee = ? AND d.niveau = 'MSN' AND d.mission_code IS NOT NULL AND m.code IS NULL
    """, (annee,)).fetchall()

    for row in rows:
        errors.append(f"Document {row[1]} references mission {row[0]} not in nomenclature")

    return errors


def check_canonical_coverage(conn: sqlite3.Connection) -> list[str]:
    """Check that all programmes have a canonical_id."""
    warnings = []
    rows = conn.execute("""
        SELECT annee, code, libelle
        FROM programme
        WHERE canonical_id IS NULL
        ORDER BY annee, code
    """).fetchall()

    for row in rows:
        warnings.append(f"Programme {row[1]} ({row[2]}) in {row[0]} has no canonical_id")
    return warnings


def check_data_stats(conn: sqlite3.Connection, annee: int) -> dict:
    """Return summary statistics for loaded data."""
    stats = {}

    row = conn.execute(
        "SELECT COUNT(*) FROM donnees_budget WHERE annee = ?", (annee,)
    ).fetchone()
    stats["data_rows"] = row[0]

    row = conn.execute(
        "SELECT COUNT(DISTINCT programme_code) FROM donnees_budget WHERE annee = ?", (annee,)
    ).fetchone()
    stats["programmes_in_data"] = row[0]

    row = conn.execute(
        "SELECT COUNT(*) FROM programme WHERE annee = ?", (annee,)
    ).fetchone()
    stats["programmes_in_nomenclature"] = row[0]

    row = conn.execute(
        "SELECT COUNT(*) FROM mission WHERE annee = ?", (annee,)
    ).fetchone()
    stats["missions"] = row[0]

    row = conn.execute(
        "SELECT COUNT(*) FROM action WHERE annee = ?", (annee,)
    ).fetchone()
    stats["actions"] = row[0]

    row = conn.execute(
        "SELECT COUNT(*) FROM document WHERE annee = ?", (annee,)
    ).fetchone()
    stats["documents"] = row[0]

    row = conn.execute(
        "SELECT SUM(ae), SUM(cp) FROM donnees_budget WHERE annee = ? AND ae IS NOT NULL", (annee,)
    ).fetchone()
    stats["total_ae"] = row[0]
    stats["total_cp"] = row[1]

    return stats


def run_all_checks(conn: sqlite3.Connection, annee: int) -> dict:
    """Run all validation checks and return a full report."""
    report = {
        "annee": annee,
        "stats": check_data_stats(conn, annee),
        "referential_integrity": check_referential_integrity(conn, annee),
        "completeness": check_completeness(conn, annee),
        "document_coverage": check_document_coverage(conn, annee),
        "canonical_coverage": check_canonical_coverage(conn),
    }

    total_errors = (
        len(report["referential_integrity"])
        + len(report["document_coverage"])
    )
    total_warnings = (
        len(report["completeness"])
        + len(report["canonical_coverage"])
    )
    report["summary"] = {
        "errors": total_errors,
        "warnings": total_warnings,
        "status": "OK" if total_errors == 0 else "ERRORS",
    }
    return report
