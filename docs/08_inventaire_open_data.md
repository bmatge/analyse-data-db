# Inventaire des données open data disponibles

## Sources data.gouv.fr

Tous les fichiers sont publiés par les Ministères économiques et financiers.

### Datasets par année

| Année | Dataset ID | Type | Ressources |
|-------|-----------|------|------------|
| 2019 | `5bbf72438b4c417355377505` | PAP Performance | PAP (indicateurs) |
| 2020 | `5da901289ce2e7311252078d` | PLF complet | Credits, Emplois, Nomenclature, Dépenses fiscales, Taxes affectées |
| 2021 | `5f7d06fcf556dc7cf57ce91e` | PLF complet | Credits, Emplois, Nomenclature, Dépenses fiscales, Taxes affectées |
| 2022 | `615f8a941a0a3faec8b0681a` | PLF complet | Credits, Emplois, Nomenclature, Dépenses fiscales, Taxes affectées |
| 2023 | — | **Non trouvé** | — |
| 2024 | `655d452025f7f2a6f3a6435b` | Dépenses dest+nature | Credits (format 2024+) |
| 2025 | `6709bd51daeddce062e00b22` | Dépenses dest+nature | Credits (format 2024+) |
| 2026 | `6916717fd1613a14a77b95df` | Budget vert uniquement | Pas de crédits |

### Fichiers téléchargés (`entrants/plf open data/`)

#### Crédits (AE/CP par destination × nature)
| Fichier | Année | Lignes | Colonnes clés |
|---------|-------|--------|---------------|
| `PLF_2020_Credits.csv` | 2020 | 2 216 | exercice, loi, typeBudget, ministere, mission, programme, action, sous_action, categorie, titre, aePlfNp1, cpPlfNp1 |
| `PLF_2021_Credits.csv` | 2021 | 2 356 | idem, colonnes: AE PLF, CP PLF |
| `PLF_2022_Credits_Destination_Nature.csv` | 2022 | 2 376 | idem, colonnes: ae, cp |
| `plf-2024-depenses-*.csv` | 2024 | 2 393 | Format différent : Type Mission, Mission, Code Mission, Programme, Libellé Programme, etc. + AE PLF, CP PLF, AE Prev FDC/ADP, CP Prev FDC/ADP, Ministère |
| `plf25-depenses-*.csv` | 2025 | 2 416 | Identique 2024 |

#### Emplois (ETPT par programme)
| Fichier | Année | Lignes | Colonnes |
|---------|-------|--------|----------|
| `PLF_2020_Emplois.csv` | 2020 | 52 | Exercice, loi, typeBudget, ministere, mission, programme, etp |
| `PLF_2021_Emplois.csv` | 2021 | 54 | idem |
| `PLF_2022_Emplois.csv` | 2022 | 54 | idem |

#### Nomenclature (hiérarchie complète)
| Fichier | Année | Lignes | Format |
|---------|-------|--------|--------|
| `PLF 2019 Nomenclature par destination.csv` | 2019 | 721 | Destination uniquement (10 col, latin-1) |
| `PLF_2020_Nomenclature.csv` | 2020 | 2 487 | Format XLS (TTR/CAT/MIN/MSN/PGM/ACT/SSA) |
| `PLF_2021_Nomenclature.csv` | 2021 | 2 584 | idem |
| `PLF_2022_Nomenclature.csv` | 2022 | 2 649 | idem |

#### Dépenses fiscales
| Fichier | Année | Lignes | Contenu |
|---------|-------|--------|---------|
| `PLF_2020_Depenses_fiscales.csv` | 2020 | 469 | Catalogue des niches fiscales par catégorie d'impôt |
| `PLF_2021_Depenses_fiscales.csv` | 2021 | 479 | idem |
| `PLF_2022_Depenses_fiscales.csv` | 2022 | 71 | Top 8 uniquement (xlsx converti) |

#### Taxes affectées
| Fichier | Année | Lignes | Contenu |
|---------|-------|--------|---------|
| `PLF_2020_Taxes_affectees.csv` | 2020 | 309 | Bénéficiaire, taxe, mission, programme, montants exécution/plafond |
| `PLF_2021_Taxes_affectees.csv` | 2021 | 290 | idem |
| `PLF_2022_Taxes_affectees.csv` | 2022 | 266 | idem |

#### Performance (indicateurs)
| Fichier | Année | Lignes | Contenu |
|---------|-------|--------|---------|
| `PLF_2019_PAP.csv` | 2019 | 1 966 | Objectifs, indicateurs, sous-indicateurs, réalisations, prévisions |

### Trous dans les données

- **PLF 2023** : aucun dataset de crédits/nomenclature trouvé sur data.gouv.fr
- **PLF 2019** : pas de fichier de crédits (AE/CP), seulement nomenclature + performance
- **PLF 2026** : uniquement Budget vert pour le moment

### Évolution des formats

| Période | Format crédits | Format nomenclature |
|---------|---------------|---------------------|
| 2020-2022 | Codes uniquement (pas de libellés), montants avec espaces, colonnes camelCase (`typeBudget`, `aePlfNp1`) | Format XLS complet (TTR/CAT/MIN/MSN/PGM/ACT/SSA) |
| 2024-2025 | Codes + libellés + Ministère en texte, colonnes lisibles (`Type Mission`, `AE PLF`), inclut FDC/ADP | Non fourni séparément (nomenclature intégrée dans les crédits) |
