"""Generate sankey_data.json for the nomenclature inter-annual Sankey visualization.

Reads from the SQLite database and produces a JSON file with:
- years, missions, programmes_data, actions_data per year
- flows (which entities persist from year to year)
- ae_by_mission, ae_by_programme per year
"""

import json
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "db" / "budget.db"
OUTPUT = PROJECT_ROOT / "src" / "web" / "static" / "sankey_data.json"


def main():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    # Get available years from nomenclature
    years = [r[0] for r in conn.execute(
        "SELECT DISTINCT annee FROM programme ORDER BY annee"
    ).fetchall()]
    print(f"Years: {years}")

    missions = {}
    programmes_data = {}
    actions_data = {}
    ae_by_mission = {}
    ae_by_programme = {}

    for year in years:
        y = str(year)

        # Missions with programme count
        rows = conn.execute("""
            SELECT m.code, m.libelle, m.type_budget,
                   COUNT(DISTINCT p.code) as nb_pgm
            FROM mission m
            LEFT JOIN programme p ON p.annee = m.annee AND p.mission_code = m.code
            WHERE m.annee = ?
            GROUP BY m.code
            ORDER BY m.type_budget, m.code
        """, (year,)).fetchall()
        missions[y] = [dict(r) for r in rows]

        # Programmes with action count
        rows = conn.execute("""
            SELECT p.code, p.libelle, p.mission_code, p.type_budget,
                   COUNT(DISTINCT a.code) as nb_act
            FROM programme p
            LEFT JOIN action a ON a.annee = p.annee AND a.programme_code = p.code
            WHERE p.annee = ?
            GROUP BY p.code
            ORDER BY p.mission_code, p.code
        """, (year,)).fetchall()
        programmes_data[y] = [dict(r) for r in rows]

        # Actions
        rows = conn.execute("""
            SELECT a.programme_code, a.code, a.libelle,
                   p.mission_code, p.type_budget
            FROM action a
            JOIN programme p ON p.annee = a.annee AND p.code = a.programme_code
            WHERE a.annee = ?
            ORDER BY p.mission_code, a.programme_code, a.code
        """, (year,)).fetchall()
        actions_data[y] = [dict(r) for r in rows]

        # AE by mission (sum across all exercices for this year)
        rows = conn.execute("""
            SELECT mission_code, SUM(ae) as total_ae
            FROM donnees_budget
            WHERE annee = ? AND ae IS NOT NULL
            GROUP BY mission_code
        """, (year,)).fetchall()
        ae_by_mission[y] = {r["mission_code"]: r["total_ae"] for r in rows if r["mission_code"]}

        # AE by programme
        rows = conn.execute("""
            SELECT programme_code, SUM(ae) as total_ae
            FROM donnees_budget
            WHERE annee = ? AND ae IS NOT NULL
            GROUP BY programme_code
        """, (year,)).fetchall()
        ae_by_programme[y] = {str(r["programme_code"]): r["total_ae"] for r in rows if r["programme_code"]}

    # Build flows: track which codes persist between consecutive years
    flows_mission = []
    flows_programme = []
    flows_action = []

    sorted_years = sorted(years)
    for i in range(len(sorted_years) - 1):
        y1, y2 = sorted_years[i], sorted_years[i + 1]
        s1, s2 = str(y1), str(y2)

        # Mission flows
        codes1 = {m["code"] for m in missions[s1]}
        codes2 = {m["code"] for m in missions[s2]}
        for code in codes1 & codes2:
            m = next(m for m in missions[s2] if m["code"] == code)
            flows_mission.append({
                "from_year": y1, "to_year": y2,
                "code": code, "value": m["nb_pgm"]
            })

        # Programme flows
        pgm_by_code1 = {p["code"]: p for p in programmes_data[s1]}
        pgm_by_code2 = {p["code"]: p for p in programmes_data[s2]}
        for code in set(pgm_by_code1) & set(pgm_by_code2):
            p1, p2 = pgm_by_code1[code], pgm_by_code2[code]
            flows_programme.append({
                "from_year": y1, "to_year": y2,
                "code": code,
                "from_parent": p1["mission_code"],
                "to_parent": p2["mission_code"],
                "value": max(p2["nb_act"], 1),
                "moved": p1["mission_code"] != p2["mission_code"]
            })

        # Action flows
        act_keys1 = {(a["programme_code"], a["code"]) for a in actions_data[s1]}
        act_keys2 = {(a["programme_code"], a["code"]) for a in actions_data[s2]}
        for key in act_keys1 & act_keys2:
            a2 = next(a for a in actions_data[s2] if (a["programme_code"], a["code"]) == key)
            flows_action.append({
                "from_year": y1, "to_year": y2,
                "programme_code": key[0], "code": key[1],
                "parent": a2["mission_code"], "value": 1
            })

    result = {
        "years": sorted_years,
        "missions": missions,
        "programmes_data": programmes_data,
        "actions_data": actions_data,
        "flows": {
            "mission": flows_mission,
            "programme": flows_programme,
            "action": flows_action,
        },
        "ae_by_mission": ae_by_mission,
        "ae_by_programme": ae_by_programme,
    }

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False)
    print(f"Written {OUTPUT} ({OUTPUT.stat().st_size // 1024} KB)")
    print(f"  {len(sorted_years)} years, {sum(len(v) for v in missions.values())} missions total")
    print(f"  {len(flows_mission)} mission flows, {len(flows_programme)} programme flows, {len(flows_action)} action flows")

    conn.close()


if __name__ == "__main__":
    main()
