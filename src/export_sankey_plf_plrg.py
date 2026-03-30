"""Generate sankey_plf_lfi_data.json for the PLF/PLRG Sankey visualization.

Shows the flow from PLF (budget proposal) to PLRG (execution results)
and between years. Uses data from donnees_budget table.
"""

import json
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "db" / "budget.db"
OUTPUT = PROJECT_ROOT / "src" / "web" / "static" / "sankey_plf_lfi_data.json"


def main():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    # Get available (annee, exercice) pairs with budget data
    pairs = conn.execute("""
        SELECT DISTINCT annee, exercice FROM donnees_budget
        WHERE ae IS NOT NULL
        ORDER BY annee, exercice
    """).fetchall()

    # Build steps in chronological order: PLR before PLF for same budget year,
    # but PLR N comes after PLF N (execution follows proposal)
    # Logical order: PLF 2024 → PLR 2024 → PLF 2025 → PLR 2025 → PLF 2026
    steps = []
    for annee, exercice in pairs:
        steps.append({"exercice": exercice, "year": annee})

    # Sort: by year, then PLF before PLR within same year
    exercice_order = {"PLF": 0, "LFI": 1, "PLR": 2}
    steps.sort(key=lambda s: (s["year"], exercice_order.get(s["exercice"], 1)))

    print(f"Steps: {[(s['exercice'], s['year']) for s in steps]}")

    missions_by_step = {}
    programmes_by_step = {}
    mission_labels = {}

    for step in steps:
        annee, exercice = step["year"], step["exercice"]
        label = f"{'PLRG' if exercice == 'PLR' else exercice} {annee}"
        step_key = f"{exercice} {annee}"

        # Missions: AE/CP aggregated
        rows = conn.execute("""
            SELECT d.mission_code,
                   SUM(d.ae) as ae, SUM(d.cp) as cp,
                   COUNT(DISTINCT d.programme_code) as nb_pgm
            FROM donnees_budget d
            WHERE d.annee = ? AND d.exercice = ? AND d.ae IS NOT NULL
            GROUP BY d.mission_code
            ORDER BY SUM(d.ae) DESC
        """, (annee, exercice)).fetchall()

        missions_by_step[step_key] = {}
        for r in rows:
            if r["mission_code"]:
                missions_by_step[step_key][r["mission_code"]] = {
                    "ae": r["ae"],
                    "cp": r["cp"],
                    "nb_pgm": r["nb_pgm"]
                }

        # Programmes: AE/CP
        rows = conn.execute("""
            SELECT d.programme_code, d.mission_code,
                   SUM(d.ae) as ae, SUM(d.cp) as cp
            FROM donnees_budget d
            WHERE d.annee = ? AND d.exercice = ? AND d.ae IS NOT NULL
            GROUP BY d.programme_code
        """, (annee, exercice)).fetchall()

        programmes_by_step[step_key] = {}
        for r in rows:
            if r["programme_code"]:
                programmes_by_step[step_key][str(r["programme_code"])] = {
                    "ae": r["ae"],
                    "cp": r["cp"],
                    "mission": r["mission_code"]
                }

        # Collect mission labels
        msn_rows = conn.execute(
            "SELECT code, libelle FROM mission WHERE annee = ?", (annee,)
        ).fetchall()
        for r in msn_rows:
            if r["code"] not in mission_labels or not mission_labels[r["code"]]:
                mission_labels[r["code"]] = r["libelle"]

    result = {
        "steps": steps,
        "missions_by_step": missions_by_step,
        "programmes_by_step": programmes_by_step,
        "mission_labels": mission_labels,
    }

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False)

    print(f"Written {OUTPUT} ({OUTPUT.stat().st_size // 1024} KB)")
    print(f"  {len(steps)} steps, {len(mission_labels)} mission labels")
    for step_key in missions_by_step:
        ms = missions_by_step[step_key]
        total_ae = sum(m["ae"] for m in ms.values() if m["ae"])
        print(f"  {step_key}: {len(ms)} missions, {len(programmes_by_step[step_key])} pgms, AE={total_ae/1e9:.0f} Md€")

    conn.close()


if __name__ == "__main__":
    main()
