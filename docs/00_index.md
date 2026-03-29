# Documentation du projet — Analyse Data & Docs du Budget

## Contexte

Projet d'analyse et de mise en relation des données budgétaires et de la documentation de la **Direction du Budget** (Bercy). Trois objectifs :

1. **Dataviz** : exploiter les données (AE/CP, ETPT, performance) pour des visualisations interactives
2. **Plan de classement** : organiser et restituer la documentation budgétaire (PAP, RAP, DPT...) de manière structurée
3. **Spécification d'interfaces** : définir les contrats API entre les bureaux métier et le site web

## Architecture

```
analyse-data-db/
├── config/                     # Configuration YAML (schemas, nomenclature, réconciliation, documents)
│   ├── schemas/                #   Mapping colonnes CSV → modèle (1 par source+année)
│   ├── reconciliation/         #   Identité canonique inter-annuelle
│   └── documents/              #   Patterns de nommage PDF
├── src/
│   ├── ingest/                 # Pipeline d'ingestion (loader, nomenclature, documents, réconciliation)
│   ├── models/                 # Schéma SQLite
│   ├── validate/               # Vérifications post-chargement
│   ├── web/                    # Site web FastAPI + DSFR
│   │   ├── app.py              #   Routes API + pages
│   │   └── static/             #   6 pages HTML + CSS + JSON dataviz
│   └── cli.py                  # Point d'entrée CLI
├── ressources/
│   ├── data/                   # 70+ CSV/XLSX open data (15 Mo, git-tracké)
│   └── docs/PLF_2025/          # 229 PDFs page de garde (8.6 Mo, git-tracké)
├── db/                         # SQLite (généré, gitignored)
├── docs/                       # Documentation technique (ce dossier)
├── entrants/                   # Sources brutes (gitignored, trop volumineux)
├── Dockerfile                  # Déploiement Docker
└── Makefile                    # Pipeline : make load-all YEAR=2025
```

## Documents de référence

| Document | Description |
|----------|-------------|
| [01 — Nomenclature budgétaire](01_nomenclature_budgetaire.md) | Hiérarchie complète : titres, ministères, missions, programmes, actions. Conventions de codes. |
| [02 — Structure des données](02_structure_donnees.md) | Les 5 jeux de données (budget, ETPT, nature, opérateurs, performance). Colonnes, sources, règles d'import. |
| [03 — Plan de classement documentaire](03_plan_classement_documentaire.md) | Arborescence des documents, types, filtres/facettes, liaison document↔données. |
| [04 — Analyse du PLF 2025](04_analyse_PLF2025.md) | Inventaire des 229 PDFs, conventions de nommage, cartographie mission→programmes. |
| [05 — Modèle de liaison Data↔Docs](05_modele_liaison_data_docs.md) | Schéma relationnel, identifiant unique, associations automatiques. |
| [06 — Datavisualisations](06_datavisualisations.md) | Bibliothèque de dataviz, indicateurs par section, structure d'un bloc. |
| [07 — Analyse Open Data PLF](07_analyse_open_data_plf.md) | Comparaison PLF 2014/2024/2025. Constantes vs variables. Stabilité des codes. |
| [08 — Inventaire Open Data](08_inventaire_open_data.md) | Catalogue complet des fichiers disponibles sur data.gouv.fr et data.economie.gouv.fr. |

## Données chargées

| Type | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|:-----|:----:|:----:|:----:|:----:|:----:|:----:|:----:|
| **PLF crédits AE/CP** | 3 259 | 2 216 | 2 356 | 2 376 | 2 321 | 2 393 | 2 416 |
| **LFI crédits AE/CP** | 2 261 | 2 241 | 2 334 | 2 352 | 2 324 | — | — |
| **Emplois ETPT** | 178 | 52 | 54 | 54 | 243 | — | — |
| **Nomenclature** | 721 | 2 487 | 2 584 | 2 649 | 2 500 | — | — |
| **Documents PDF** | — | — | — | — | — | — | 229 |
| **Performance** | 1 966 | — | — | — | — | — | 2 177 |

## Site web (6 pages)

| Page | URL | Description |
|------|-----|-------------|
| Accueil | `/` | Problématique du plan de classement, cycle budgétaire, défis, solution |
| Glossaire | `/glossaire` | Nomenclatures avec badges, abbr, tables DSFR, diagramme SVG |
| Interfaces | `/api-specs` | Spécification des 2 API (data + docs), responsabilités, calendrier |
| Nomenclature | `/nomenclature` | 2 onglets : arborescence interactive + Sankey inter-annuel |
| Corpus | `/corpus` | 229 PDFs indexés par type budget / mission / programme |
| Flux PLF/LFI | `/plf-lfi` | Sankey PLF→LFI 2019-2023 avec montants AE |

## Pipeline de publication (24h, zéro code)

```bash
# 1. Déposer les CSV dans ressources/data/
# 2. Copier config YAML (changer annee)
# 3. Lancer :
make load-all YEAR=2026
```

## Concepts clés

- La **nomenclature** est le pivot : elle relie données, documents, ministères et missions
- Les codes sont **contextuels par année** (programme 104 en 2019 ≠ programme 104 en 2024)
- Le **programme** est l'entité centrale : il porte la liaison mission + ministère
- L'**identité canonique** permet le suivi longitudinal malgré les changements de codes
- Les **noms de ministères** ne sont jamais une clé fiable (changent à chaque remaniement)
- Les données arrivent en **3 temps** : PLF (automne) → LFI (décembre) → PLR (printemps)
