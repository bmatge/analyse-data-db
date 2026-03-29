"""SQLite schema for the budget classification system."""

import sqlite3
from pathlib import Path

SCHEMA_SQL = """
-- ============================================================
-- TABLES INVARIANTES (constantes, ne changent pas d'une année à l'autre)
-- ============================================================

CREATE TABLE IF NOT EXISTS type_budget (
    code TEXT PRIMARY KEY,          -- BG, BA, CAS, CCF
    libelle TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS titre (
    code INTEGER PRIMARY KEY,       -- 1-7
    libelle TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS categorie (
    code INTEGER PRIMARY KEY,       -- 10-73
    titre_code INTEGER NOT NULL REFERENCES titre(code),
    libelle TEXT NOT NULL
);

-- ============================================================
-- NOMENCLATURE VERSIONNÉE PAR ANNÉE
-- ============================================================

CREATE TABLE IF NOT EXISTS ministere (
    annee INTEGER NOT NULL,
    code INTEGER NOT NULL,
    libelle TEXT NOT NULL,
    libelle_abrege TEXT,
    PRIMARY KEY (annee, code)
);

CREATE TABLE IF NOT EXISTS mission (
    annee INTEGER NOT NULL,
    code TEXT NOT NULL,              -- 2 lettres (AA, AB, ...)
    type_budget TEXT NOT NULL REFERENCES type_budget(code),
    libelle TEXT NOT NULL,
    libelle_abrege TEXT,
    PRIMARY KEY (annee, code)
);

CREATE TABLE IF NOT EXISTS programme (
    annee INTEGER NOT NULL,
    code INTEGER NOT NULL,           -- 3 chiffres (101-878)
    libelle TEXT NOT NULL,
    libelle_abrege TEXT,
    mission_code TEXT NOT NULL,
    ministere_code INTEGER,
    type_budget TEXT NOT NULL,
    commentaire TEXT,
    canonical_id TEXT,               -- lien vers entity_canonical
    PRIMARY KEY (annee, code)
);

CREATE TABLE IF NOT EXISTS action (
    annee INTEGER NOT NULL,
    programme_code INTEGER NOT NULL,
    code TEXT NOT NULL,               -- NN (ex: "01")
    libelle TEXT NOT NULL,
    PRIMARY KEY (annee, programme_code, code)
);

CREATE TABLE IF NOT EXISTS sous_action (
    annee INTEGER NOT NULL,
    programme_code INTEGER NOT NULL,
    action_code TEXT NOT NULL,
    code TEXT NOT NULL,
    libelle TEXT NOT NULL,
    PRIMARY KEY (annee, programme_code, action_code, code)
);

-- ============================================================
-- IDENTITÉ CANONIQUE (suivi longitudinal inter-annuel)
-- ============================================================

CREATE TABLE IF NOT EXISTS entity_canonical (
    canonical_id TEXT PRIMARY KEY,
    entity_type TEXT NOT NULL,        -- programme, mission
    label TEXT NOT NULL,
    created_year INTEGER NOT NULL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS entity_year_mapping (
    canonical_id TEXT NOT NULL REFERENCES entity_canonical(canonical_id),
    annee INTEGER NOT NULL,
    entity_type TEXT NOT NULL,
    code TEXT NOT NULL,
    libelle TEXT,
    relation TEXT DEFAULT 'same',     -- same, renamed, merged_from, split_from, moved
    PRIMARY KEY (canonical_id, annee)
);

CREATE TABLE IF NOT EXISTS entity_event (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    annee INTEGER NOT NULL,
    event_type TEXT NOT NULL,          -- merge, split, move, rename, create, delete
    source_canonical_id TEXT,
    target_canonical_id TEXT,
    description TEXT
);

-- ============================================================
-- DONNÉES BUDGÉTAIRES
-- ============================================================

CREATE TABLE IF NOT EXISTS donnees_budget (
    annee INTEGER NOT NULL,
    exercice TEXT NOT NULL,            -- PLF, LFI, PLR
    type_budget TEXT NOT NULL,
    mission_code TEXT,
    programme_code INTEGER NOT NULL,
    action_code TEXT,
    sous_action_code TEXT,
    categorie_code INTEGER,
    titre_code INTEGER,
    ae REAL,
    cp REAL,
    ae_fdc_adp REAL,
    cp_fdc_adp REAL,
    ministere_nom TEXT,
    ministere_code INTEGER,
    source_file TEXT,
    loaded_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_donnees_budget_annee_exercice
    ON donnees_budget(annee, exercice);
CREATE INDEX IF NOT EXISTS idx_donnees_budget_programme
    ON donnees_budget(annee, programme_code);

CREATE TABLE IF NOT EXISTS donnees_etpt (
    annee INTEGER NOT NULL,
    exercice TEXT NOT NULL,
    type_budget TEXT NOT NULL,
    mission_code TEXT NOT NULL,
    programme_code INTEGER NOT NULL,
    ministere_code INTEGER,
    etpt REAL,
    source_file TEXT,
    loaded_at TEXT DEFAULT (datetime('now')),
    PRIMARY KEY (annee, exercice, type_budget, programme_code)
);

-- ============================================================
-- REGISTRE DE DOCUMENTS
-- ============================================================

CREATE TABLE IF NOT EXISTS document (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    annee INTEGER NOT NULL,
    exercice TEXT NOT NULL,
    type_document TEXT NOT NULL,       -- PAP, RAP, DPT, Jaune...
    type_budget TEXT NOT NULL,
    niveau TEXT NOT NULL,              -- MSN ou PGM
    mission_code TEXT,
    programme_code INTEGER,
    ministere_code INTEGER,
    filename TEXT NOT NULL,
    filepath TEXT NOT NULL,
    titre TEXT,
    loaded_at TEXT DEFAULT (datetime('now')),
    UNIQUE (annee, exercice, type_document, type_budget, niveau,
            mission_code, programme_code)
);

-- ============================================================
-- MÉTADONNÉES DE CHARGEMENT
-- ============================================================

CREATE TABLE IF NOT EXISTS load_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT DEFAULT (datetime('now')),
    operation TEXT NOT NULL,           -- load_data, load_nomenclature, load_documents, reconcile
    annee INTEGER,
    exercice TEXT,
    source_file TEXT,
    rows_loaded INTEGER,
    status TEXT NOT NULL,              -- success, error
    message TEXT
);
"""


def init_db(db_path: str) -> sqlite3.Connection:
    """Create the database and all tables."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    return conn


def get_connection(db_path: str) -> sqlite3.Connection:
    """Get a connection to an existing database."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    return conn
