# Documentation du projet — Analyse Data & Docs du Budget

## Contexte

Projet d'analyse et de mise en relation des données budgétaires et de la documentation de la **Direction du Budget** (Bercy). Deux objectifs :

1. **Dataviz** : exploiter les données (AE/CP, ETPT, performance, opérateurs) pour des visualisations
2. **Plan de classement** : organiser et restituer la documentation budgétaire (PAP, RAP, DPT...) de manière structurée et navigable

## Documents de référence

| Document | Description |
|----------|-------------|
| [01 — Nomenclature budgétaire](01_nomenclature_budgetaire.md) | Structure hiérarchique complète : titres, ministères, missions, programmes, actions, sous-actions. Conventions de codes. |
| [02 — Structure des données](02_structure_donnees.md) | Les 5 jeux de données (budget, ETPT, nature, opérateurs, performance). Colonnes, sources, règles d'import. |
| [03 — Plan de classement documentaire](03_plan_classement_documentaire.md) | Arborescence des documents, types de documents, filtres/facettes, liaison document↔données. |
| [04 — Analyse du PLF 2025](04_analyse_PLF2025.md) | Inventaire des 229 PDFs du PLF 2025, conventions de nommage, cartographie mission→programmes. |
| [05 — Modèle de liaison Data↔Docs](05_modele_liaison_data_docs.md) | Schéma relationnel, identifiant unique d'un document, associations automatiques, dimensions de navigation. |
| [06 — Datavisualisations](06_datavisualisations.md) | Bibliothèque de types de dataviz, indicateurs par section, structure d'un bloc dataviz. |
| [07 — Analyse Open Data PLF](07_analyse_open_data_plf.md) | Comparaison des PLF 2014/2024/2025 open data. Constantes vs variables. Stabilité des codes. |

## Sources en entrée

```
entrants/
├── documentation/
│   ├── DB_Specifications_fonctionnelles_Final.pdf   # Spécifications fonctionnelles (Avril 2019)
│   ├── Nomenclature_0510_10h(3).xls                 # Table de nomenclature (2021)
│   ├── Nomenclature_0510_FULL_DUMP.csv               # Export CSV de la nomenclature
│   ├── BUDGET_D8_GUIDE_UTILISATEUR_v1.4.pdf          # Guide utilisateur Drupal
│   ├── exemple_import_indicateur.zip                 # Exemple d'import
│   └── documentation site DB.zip                     # Documentation supplémentaire
├── PLF_2025/                                         # 229 PDFs des PAP du PLF 2025
│   ├── BG/ BA/ CAS/ CCF/ CCO/ COM/                   # Par type de budget
│   ├── fichiers.csv                                   # Index des fichiers
│   └── list.txt                                       # Arborescence
└── plf open data/                                     # Données open data (CSV)
    ├── plf-2014-nomenclature-par-destination.csv      # Nomenclature seule (7 col, 722 lignes)
    ├── plf-2024-depenses-...-destination-et-nature.csv # Nomenclature + dépenses (16 col, 2392 lignes)
    └── plf25-depenses-...-destination-et-nature.csv   # Idem 2025 (16 col, 2415 lignes)
```

## Concepts clés à retenir

- La **nomenclature** est la pierre angulaire : elle relie données, documents, ministères et missions
- Les codes sont **contextuels par année** (un même numéro de programme peut changer de signification)
- Le **type de budget** s'encode dans le code mission (A-V = BG, X = BA, Y = CAS, Z = CCF)
- Le **programme** est l'entité pivot qui porte la liaison mission + ministère
- Les données arrivent en **3 temps** par an : PLF → LFI → PLR

## Constantes vs Variables (enseignements de l'analyse open data)

### Éléments stables (constantes)
- La hiérarchie Mission → Programme → Action → Sous-action
- Les 4 types de budget (BG, BA, CAS, CCF)
- Les 7 titres et 19 catégories de dépenses
- **133 codes programme** stables sur 10 ans (2014→2025)
- **35 missions** stables sur 10 ans

### Éléments instables (variables)
- **Noms de ministères** : changent à chaque remaniement (ne jamais utiliser comme clé)
- **Missions** : rares créations/fusions/scissions (ex: audiovisuel public passé de CAS à BG en 2025)
- **Programmes** : 57 supprimés, ~30 créés, 22 renommés entre 2014 et 2025
- **Schéma des fichiers open data** : a radicalement changé entre 2014 (7 col) et 2024 (16 col)
- **Sous-actions** : ~75% de valeurs nulles, granularité non fiable
