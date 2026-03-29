"""Export Sankey data for PLF→LFI flow visualization (2019-2023)."""

import csv
import json
import sys
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "entrants" / "plf open data"
OUT_FILE = Path(__file__).parent.parent / "docs" / "sankey_plf_lfi_data.json"


def parse_int(val):
    """Parse an integer that may have spaces as thousands separator."""
    if val is None:
        return 0
    val = str(val).strip().replace(" ", "").replace("\u00a0", "").replace(",", ".")
    if not val or val == "nan":
        return 0
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return 0


def load_plf_2019():
    """PLF 2019: multiple files per budget type, latin-1 encoding."""
    records = []
    files = [
        ("PLF_2019_BG_Nature.csv", "latin-1"),
        ("PLF_2019_CS_Nature.csv", "latin-1"),
        ("PLF_2019_CCF_Nature.csv", "latin-1"),
    ]
    for fname, enc in files:
        path = DATA_DIR / fname
        if not path.exists():
            continue
        with open(path, encoding=enc, newline="") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                mission = row.get("Code Mission", "").strip()
                programme = row.get("Code Programme", "").strip()
                if not programme:
                    continue
                ae = parse_int(row.get("AE PLF 2019"))
                cp = parse_int(row.get("CP PLF 2019"))
                records.append({"mission": mission, "programme": int(programme), "ae": ae, "cp": cp})
    return records


def load_plf_2020_2022(year):
    """PLF 2020-2022: single file, space-separated numbers."""
    fnames = {
        2020: "PLF_2020_Credits.csv",
        2021: "PLF_2021_Credits.csv",
        2022: "PLF_2022_Credits_Destination_Nature.csv",
    }
    ae_col = {2020: "aePlfNp1", 2021: "AE PLF", 2022: "ae"}
    cp_col = {2020: "cpPlfNp1", 2021: "CP PLF", 2022: "cp"}

    path = DATA_DIR / fnames[year]
    records = []
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            mission = row.get("mission", "").strip()
            programme = row.get("programme", "").strip()
            if not programme:
                continue
            ae = parse_int(row.get(ae_col[year]))
            cp = parse_int(row.get(cp_col[year]))
            records.append({"mission": mission, "programme": int(programme), "ae": ae, "cp": cp})
    return records


def load_plf_2023():
    """PLF 2023: similar to 2022."""
    path = DATA_DIR / "PLF_2023_Credits_Destination_Nature.csv"
    records = []
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            mission = row.get("mission", "").strip()
            programme = row.get("programme", "").strip()
            if not programme:
                continue
            ae = parse_int(row.get("ae"))
            cp = parse_int(row.get("cp"))
            records.append({"mission": mission, "programme": int(float(programme)), "ae": ae, "cp": cp})
    return records


def load_lfi_2019():
    """LFI 2019: own format with full labels."""
    path = DATA_DIR / "LFI_2019_Credits.csv"
    records = []
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            mission = row.get("Code Mission", "").strip()
            programme = row.get("Code Programme", "").strip()
            if not programme:
                continue
            ae = parse_int(row.get("AE LFI 2019"))
            cp = parse_int(row.get("CP LFI 2019"))
            records.append({"mission": mission, "programme": int(programme), "ae": ae, "cp": cp})
    return records


def load_lfi_2020():
    """LFI 2020: same format as PLF 2020 but different AE/CP column names."""
    path = DATA_DIR / "LFI_2020_Credits.csv"
    records = []
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            mission = row.get("mission", "").strip()
            programme = row.get("programme", "").strip()
            if not programme:
                continue
            ae = parse_int(row.get("AE LFI 2020"))
            cp = parse_int(row.get("CP LFI 2020"))
            records.append({"mission": mission, "programme": int(programme), "ae": ae, "cp": cp})
    return records


def load_lfi_2021_2023(year):
    """LFI 2021-2023: rich format with PLF+amendments+LFI, T2/HT2 split."""
    fnames = {
        2021: "LFI_2021_Credits.csv",
        2022: "LFI_2022_Credits.csv",
        2023: "LFI_2023_Credits_Destination_Nature.csv",
    }
    # Column names vary slightly
    ae_lfi_cols = {
        2021: "AE ( T2 + HT2) LFI",
        2022: "AE ( T2 + HT2) LFI",
        2023: "AE (T2 + Hors T2) LFI  2023",
    }
    cp_lfi_cols = {
        2021: "CP ( T2 + HT2) LFI",
        2022: "CP ( T2 + HT2) LFI",
        2023: "CP (T2 + Hors T2) LFI  2023",
    }

    path = DATA_DIR / fnames[year]
    # Try different encodings
    for enc in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            with open(path, encoding=enc, newline="") as f:
                reader = csv.DictReader(f, delimiter=";")
                fields = reader.fieldnames
                if fields:
                    break
        except UnicodeDecodeError:
            continue

    records = []
    with open(path, encoding=enc, newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        # Find the right column names by fuzzy match
        ae_col = None
        cp_col = None
        for col in reader.fieldnames:
            col_clean = col.strip()
            if "AE" in col_clean and "LFI" in col_clean and ("T2 + H" in col_clean or "T2 + HT2" in col_clean or "T2 + Hors" in col_clean):
                ae_col = col
            if "CP" in col_clean and "LFI" in col_clean and ("T2 + H" in col_clean or "T2 + HT2" in col_clean or "T2 + Hors" in col_clean):
                cp_col = col

        # For 2023: LFI columns are flags (all 4.0), compute LFI = PLF + Amendments
        use_plf_plus_amd = False
        if ae_col and cp_col:
            # Quick check: if all LFI values are 4.0, it's a flag
            f.seek(0)
            test_reader = csv.DictReader(f, delimiter=";")
            sample_vals = set()
            for i, row in enumerate(test_reader):
                if i >= 20:
                    break
                v = row.get(ae_col, "").strip()
                if v:
                    sample_vals.add(v)
            if sample_vals == {"4.0"} or sample_vals == {"4"}:
                use_plf_plus_amd = True
                print(f"  LFI columns are flags, computing LFI = PLF + Amendements")

        if not ae_col or not cp_col:
            print(f"  WARNING: Could not find AE/CP LFI columns in {fnames[year]}")
            return []

        f.seek(0)
        reader = csv.DictReader(f, delimiter=";")

        # Find PLF and Amendment column names for fallback
        ae_plf_t2 = ae_plf_ht2 = ae_amd_t2 = ae_amd_ht2 = None
        cp_plf_t2 = cp_plf_ht2 = cp_amd_t2 = cp_amd_ht2 = None
        for col in reader.fieldnames:
            c = col.strip()
            if "AE" in c and "T2" in c and "PLF" in c and "Hors" not in c:
                ae_plf_t2 = col
            if "AE" in c and "PLF" in c and ("Hors T2" in c or "HT2" in c) and "+" not in c:
                ae_plf_ht2 = col
            if "AE" in c and "T2" in c and ("Amend" in c or "AMD" in c or "amd" in c) and "Hors" not in c:
                ae_amd_t2 = col
            if "AE" in c and ("Amend" in c or "AMD" in c or "amd" in c) and ("Hors" in c or "HT2" in c) and "+" not in c:
                ae_amd_ht2 = col
            if "CP" in c and "T2" in c and "PLF" in c and "Hors" not in c:
                cp_plf_t2 = col
            if "CP" in c and "PLF" in c and ("Hors T2" in c or "HT2" in c) and "+" not in c:
                cp_plf_ht2 = col
            if "CP" in c and "T2" in c and ("Amend" in c or "AMD" in c or "amd" in c) and "Hors" not in c:
                cp_amd_t2 = col
            if "CP" in c and ("Amend" in c or "AMD" in c or "amd" in c) and ("Hors" in c or "HT2" in c) and "+" not in c:
                cp_amd_ht2 = col

        f.seek(0)
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            mission = row.get("Code Mission", row.get("mission", "")).strip()
            programme = row.get("Programme", row.get("programme", "")).strip()
            if not programme:
                continue
            try:
                pgm_code = int(float(programme))
            except (ValueError, TypeError):
                continue

            if use_plf_plus_amd:
                ae = (parse_int(row.get(ae_plf_t2)) + parse_int(row.get(ae_plf_ht2))
                      + parse_int(row.get(ae_amd_t2)) + parse_int(row.get(ae_amd_ht2)))
                cp = (parse_int(row.get(cp_plf_t2)) + parse_int(row.get(cp_plf_ht2))
                      + parse_int(row.get(cp_amd_t2)) + parse_int(row.get(cp_amd_ht2)))
            else:
                ae = parse_int(row.get(ae_col))
                cp = parse_int(row.get(cp_col))

            records.append({"mission": mission, "programme": pgm_code, "ae": ae, "cp": cp})
    return records


def aggregate_by_mission(records):
    """Aggregate AE/CP by mission code."""
    by_mission = {}
    for r in records:
        m = r["mission"]
        if not m:
            continue
        if m not in by_mission:
            by_mission[m] = {"ae": 0, "cp": 0, "programmes": set()}
        by_mission[m]["ae"] += r["ae"]
        by_mission[m]["cp"] += r["cp"]
        by_mission[m]["programmes"].add(r["programme"])
    # Convert sets to counts
    for m in by_mission:
        by_mission[m]["nb_pgm"] = len(by_mission[m]["programmes"])
        del by_mission[m]["programmes"]
    return by_mission


def aggregate_by_programme(records):
    """Aggregate AE/CP by programme code."""
    by_pgm = {}
    for r in records:
        p = r["programme"]
        if not p:
            continue
        if p not in by_pgm:
            by_pgm[p] = {"ae": 0, "cp": 0, "mission": r["mission"]}
        by_pgm[p]["ae"] += r["ae"]
        by_pgm[p]["cp"] += r["cp"]
    return by_pgm


def main():
    loaders = {
        ("PLF", 2019): load_plf_2019,
        ("PLF", 2020): lambda: load_plf_2020_2022(2020),
        ("PLF", 2021): lambda: load_plf_2020_2022(2021),
        ("PLF", 2022): lambda: load_plf_2020_2022(2022),
        ("PLF", 2023): load_plf_2023,
        ("LFI", 2019): load_lfi_2019,
        ("LFI", 2020): load_lfi_2020,
        ("LFI", 2021): lambda: load_lfi_2021_2023(2021),
        ("LFI", 2022): lambda: load_lfi_2021_2023(2022),
        ("LFI", 2023): lambda: load_lfi_2021_2023(2023),
    }

    # Ordered steps: PLF 2019 → LFI 2019 → PLF 2020 → LFI 2020 → ...
    steps = []
    for year in [2019, 2020, 2021, 2022, 2023]:
        steps.append(("PLF", year))
        steps.append(("LFI", year))

    data = {
        "steps": [{"exercice": ex, "year": y} for ex, y in steps],
        "missions_by_step": {},
        "programmes_by_step": {},
        "mission_labels": {},
    }

    # Load all data
    for ex, year in steps:
        key = f"{ex} {year}"
        print(f"Loading {key}...")
        records = loaders[(ex, year)]()
        print(f"  {len(records)} records")

        by_mission = aggregate_by_mission(records)
        by_programme = aggregate_by_programme(records)

        data["missions_by_step"][key] = {
            m: {"ae": v["ae"], "cp": v["cp"], "nb_pgm": v["nb_pgm"]}
            for m, v in by_mission.items()
        }
        data["programmes_by_step"][key] = {
            str(p): {"ae": v["ae"], "cp": v["cp"], "mission": v["mission"]}
            for p, v in by_programme.items()
        }

        total_ae = sum(v["ae"] for v in by_mission.values())
        print(f"  {len(by_mission)} missions, {len(by_programme)} programmes, AE total: {total_ae/1e9:.1f} Md€")

    # Collect mission labels from the database if available
    try:
        import sqlite3
        db_path = Path(__file__).parent.parent / "db" / "budget.db"
        conn = sqlite3.connect(str(db_path))
        rows = conn.execute("SELECT DISTINCT code, libelle FROM mission WHERE libelle != '' ORDER BY code").fetchall()
        for code, libelle in rows:
            data["mission_labels"][code] = libelle
        conn.close()
    except Exception:
        pass

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    print(f"\nExported to {OUT_FILE}")


if __name__ == "__main__":
    main()
