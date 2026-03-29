"""Cross-year entity reconciliation engine."""

import sqlite3

import yaml


def load_reconciliation_config(config_path: str) -> dict:
    """Load the reconciliation YAML config."""
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_canonical_entities(conn: sqlite3.Connection, config_path: str) -> dict:
    """Build canonical entities and year mappings from the reconciliation config.

    Returns a summary of what was created.
    """
    config = load_reconciliation_config(config_path)
    stats = {"canonical_created": 0, "mappings_created": 0, "events_created": 0}

    # 1. Stable codes: create canonical entries for programmes that kept the same code
    stable_codes = config.get("stable_codes", {}).get("codes", [])
    for code in stable_codes:
        canonical_id = f"PGM:{code}"

        # Get the most recent label for this programme
        row = conn.execute(
            "SELECT libelle FROM programme WHERE code = ? ORDER BY annee DESC LIMIT 1",
            (code,),
        ).fetchone()
        label = row[0] if row else f"Programme {code}"

        # Get earliest year
        row_year = conn.execute(
            "SELECT MIN(annee) FROM programme WHERE code = ?",
            (code,),
        ).fetchone()
        created_year = row_year[0] if row_year and row_year[0] else 2014

        conn.execute(
            "INSERT OR IGNORE INTO entity_canonical (canonical_id, entity_type, label, created_year) "
            "VALUES (?, 'programme', ?, ?)",
            (canonical_id, label, created_year),
        )
        stats["canonical_created"] += 1

        # Create year mappings for all years this programme exists
        years = conn.execute(
            "SELECT annee, libelle FROM programme WHERE code = ? ORDER BY annee",
            (code,),
        ).fetchall()
        for year_row in years:
            conn.execute(
                "INSERT OR IGNORE INTO entity_year_mapping "
                "(canonical_id, annee, entity_type, code, libelle, relation) "
                "VALUES (?, ?, 'programme', ?, ?, 'same')",
                (canonical_id, year_row[0], str(code), year_row[1]),
            )
            stats["mappings_created"] += 1

        # Update programme table with canonical_id
        conn.execute(
            "UPDATE programme SET canonical_id = ? WHERE code = ?",
            (canonical_id, code),
        )

    # 2. Programmes created between 2014 and 2024
    for section_key in ("created_2014_2024", "created_2025"):
        section = config.get(section_key, {})
        codes = section.get("codes", [])
        for code in codes:
            canonical_id = f"PGM:{code}"
            row = conn.execute(
                "SELECT libelle, MIN(annee) FROM programme WHERE code = ? GROUP BY code",
                (code,),
            ).fetchone()
            if not row:
                continue
            label, created_year = row[0], row[1]

            conn.execute(
                "INSERT OR IGNORE INTO entity_canonical (canonical_id, entity_type, label, created_year) "
                "VALUES (?, 'programme', ?, ?)",
                (canonical_id, label, created_year),
            )
            stats["canonical_created"] += 1

            years = conn.execute(
                "SELECT annee, libelle FROM programme WHERE code = ? ORDER BY annee",
                (code,),
            ).fetchall()
            for year_row in years:
                conn.execute(
                    "INSERT OR IGNORE INTO entity_year_mapping "
                    "(canonical_id, annee, entity_type, code, libelle, relation) "
                    "VALUES (?, ?, 'programme', ?, ?, 'same')",
                    (canonical_id, year_row[0], str(code), year_row[1]),
                )
                stats["mappings_created"] += 1

            conn.execute(
                "UPDATE programme SET canonical_id = ? WHERE code = ?",
                (canonical_id, code),
            )

    # 3. Process events (renames, moves, etc.)
    events = config.get("events", [])
    for event in events:
        event_type = event.get("type")
        year = event.get("year")
        description = event.get("description", event.get("note", ""))

        if event_type == "rename":
            code = event.get("code")
            canonical_id = f"PGM:{code}"
            conn.execute(
                "INSERT INTO entity_event (annee, event_type, source_canonical_id, description) "
                "VALUES (?, 'rename', ?, ?)",
                (year, canonical_id, f"{event.get('old_label')} → {event.get('new_label')}"),
            )
            stats["events_created"] += 1

        elif event_type == "move":
            sources = event.get("sources", [])
            targets = event.get("targets", [])
            for target in targets:
                cid = target.get("canonical_id", f"PGM:{target['code']}")
                conn.execute(
                    "INSERT OR IGNORE INTO entity_canonical (canonical_id, entity_type, label, created_year) "
                    "VALUES (?, 'programme', ?, ?)",
                    (cid, target.get("label", f"Programme {target['code']}"), year),
                )
                # Find the source this target replaces
                source_desc = ", ".join(f"{s['code']} ({s.get('label', '')})" for s in sources)
                conn.execute(
                    "INSERT INTO entity_event (annee, event_type, source_canonical_id, target_canonical_id, description) "
                    "VALUES (?, 'move', ?, ?, ?)",
                    (year, source_desc, cid, description),
                )
                stats["events_created"] += 1

        elif event_type == "split":
            conn.execute(
                "INSERT INTO entity_event (annee, event_type, description) VALUES (?, 'split', ?)",
                (year, description),
            )
            stats["events_created"] += 1

    conn.commit()

    # 4. Report unmatched programmes (no canonical_id)
    unmatched = conn.execute(
        "SELECT annee, code, libelle FROM programme WHERE canonical_id IS NULL ORDER BY annee, code"
    ).fetchall()

    return {
        **stats,
        "unmatched_programmes": [(r[0], r[1], r[2]) for r in unmatched],
    }
