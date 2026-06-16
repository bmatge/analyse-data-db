# analyse-data-db — Analyse Data & Docs du Budget

> POC pour le **portail web de la Direction du Budget** (Bercy) : mettre en relation les **données budgétaires** et la **documentation** de l'État, en simulant les montages data/documentaires de l'application **TANGO** et la **nomenclature budgétaire** spécifique du budget de l'État (BG/BA/CAS/CCF, titres, AE/CP, ETPT…).

## Objectifs

1. **Dataviz** — exploiter les données (AE/CP, ETPT, performance) en visualisations interactives (Sankey, etc.).
2. **Plan de classement** — organiser et restituer la documentation budgétaire (PAP, RAP, DPT…) de façon structurée.
3. **Spécification d'interfaces** — définir les contrats API entre les bureaux métier et le site web.

## Stack

Python **FastAPI** + **DSFR** (site web), **SQLite** (modèle), **pandas**/PyYAML (pipeline d'ingestion), **Docker** + **Makefile**. Aucune dépendance front lourde.

## Architecture

```
config/            Configuration YAML : schemas (mapping CSV→modèle), nomenclature,
                   réconciliation (identité canonique inter-annuelle), documents (nommage PDF)
src/
  ingest/          Pipeline d'ingestion (loader, nomenclature, documents, réconciliation)
  models/          Schéma SQLite
  validate/        Vérifications post-chargement
  web/             Site FastAPI + DSFR (app.py + static/ : pages HTML, CSS, JSON dataviz)
  cli.py           Point d'entrée CLI
ressources/        70+ CSV/XLSX open data + 229 PDF (pages de garde PLF 2025), git-trackés
docs/              Documentation technique (nomenclature, structure, plan de classement, analyses PLF/LFI)
```

## Démarrage

```bash
pip install -r requirements.txt
make load-all YEAR=2025      # ingestion open data PLF/LFI 2025
# ou via Docker : docker compose up
```

Documentation détaillée dans [`docs/`](./docs/) (index : [`docs/00_index.md`](./docs/00_index.md)).
