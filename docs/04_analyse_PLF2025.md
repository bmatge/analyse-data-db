# Analyse du corpus PLF 2025

## Vue d'ensemble

- **229 documents PDF** au total
- **46 documents mission** (MSN)
- **181 documents programme** (PGM)
- **2 documents spéciaux** (CCO, COM)
- Type : PAP (Projet Annuel de Performances) du PLF 2025

## Structure des répertoires

```
PLF_2025/
├── BG/                          # Budget général (174 PDFs)
│   ├── MSN/{code_mission}/      # 34 missions
│   └── PGM/{num_programme}/     # 140 programmes
├── BA/                          # Budgets annexes (7 PDFs)
│   ├── MSN/{code_mission}/      # 2 missions
│   └── PGM/{num_programme}/     # 5 programmes
├── CAS/                         # Comptes d'affectation spéciale (21 PDFs)
│   ├── MSN/{code_mission}/      # 6 missions
│   └── PGM/{num_programme}/     # 15 programmes
├── CCF/                         # Comptes de concours financiers (25 PDFs)
│   ├── MSN/{code_mission}/      # 4 missions
│   └── PGM/{num_programme}/     # 21 programmes
├── CCO/CCO/                     # Comptes de commerce (1 PDF global)
├── COM/COM/                     # Comptes d'opérations monétaires (1 PDF global)
├── fichiers.csv                 # Index des fichiers
├── fichiers.ods                 # Idem en ODS
└── list.txt                     # Arborescence (tree Windows)
```

## Conventions de nommage

### Fichiers MSN (mission)

**Pattern** : `PAP2025_{code_budget}_{nom_mission}_{code_mission}.pdf`

| Segment | Valeurs | Exemple |
|---------|---------|---------|
| `PAP2025` | Fixe | — |
| `code_budget` | `BG`, `BA`, `CS_CAS`, `CS_CCF`, `CS_CCO`, `CS_COM` | `BG` |
| `nom_mission` | Nom en snake_case | `Defense` |
| `code_mission` | 2 lettres majuscules | `DA` |

Note : pour CAS/CCF/CCO/COM, le préfixe dans le nom de fichier est `CS_CAS`, `CS_CCF`, etc. (pas juste `CAS`).

### Fichiers PGM (programme)

**Pattern** : `FR_2025_PLF_{code_mission}_PGM_{num_programme}.pdf`

| Segment | Valeurs | Exemple |
|---------|---------|---------|
| `FR_2025_PLF` | Fixe | — |
| `code_mission` | 2 lettres majuscules | `DA` |
| `num_programme` | 3 chiffres | `178` |

Le code mission dans le nom du fichier PGM permet de relier chaque programme à sa mission.

### Fichiers spéciaux (CCO, COM)

Pas de découpage MSN/PGM. Un seul PDF par type :
- `PAP2025_CS_CCO_Comptes_commerce.pdf`
- `PAP2025_CS_COM_Comptes_operations_monetaires.pdf`

## Cartographie complète Mission → Programmes

### BG — Budget général (34 missions, 140 programmes)

| Code | Mission | Programmes |
|------|---------|------------|
| AA | Action extérieure de l'État | 105, 151, 185 |
| AB | Administration générale et territoriale de l'État | 216, 232, 354 |
| AC | Agriculture, alimentation, forêt et affaires rurales | 149, 206, 215, 381 |
| AD | Aide publique au développement | 110, 209, 365, 370, 384 |
| AQ | Audiovisuel public | 372, 373, 374, 375, 376, 377, 383 |
| AV | Investir pour la France de 2030 | 421, 422, 423, 424, 425 |
| CA | Conseil et contrôle de l'État | 126, 164, 165 |
| CB | Culture | 131, 175, 224, 361 |
| DA | Défense | 144, 146, 178, 212 |
| DB | Économie | 134, 220, 305, 343, 367 |
| DC | Direction de l'action du Gouvernement | 129, 308 |
| EB | Engagements financiers de l'État | 114, 117, 145, 336, 338, 344, 355, 369 |
| EC | Enseignement scolaire | 139, 140, 141, 143, 214, 230 |
| GA | Gestion des finances publiques | 156, 218, 302 |
| IA | Immigration, asile et intégration | 104, 303 |
| JA | Justice | 101, 107, 166, 182, 310, 335 |
| MA | Médias, livre et industries culturelles | 180, 334 |
| MB | Anciens combattants, mémoire et liens avec la nation | 158, 169 |
| OA | Outre-mer | 123, 138 |
| PB | Pouvoirs publics | 501, 511, 521, 531, 532, 533, 541, 542 |
| PC | Crédits non répartis | 551, 552 |
| PR | Plan de relance | 362, 363 |
| RA | Recherche et enseignement supérieur | 142, 150, 172, 190, 191, 192, 193, 231 |
| RB | Régimes sociaux et de retraite | 195, 197, 198 |
| RC | Relations avec les collectivités territoriales | 119, 122 |
| RD | Remboursements et dégrèvements | 200, 201 |
| SA | Sant�� | 183, 204, 379 |
| SB | Sécurités | 152, 161, 176, 207 |
| SE | Solidarité, insertion et égalité des chances | 137, 157, 304 |
| SF | Sport, jeunesse et vie associative | 163, 219, 350 |
| TA | Écologie, développement et mobilités durables | 113, 159, 174, 181, 203, 205, 217, 235, 345, 380 |
| TB | Travail et emploi | 102, 103, 111, 155 |
| TR | Transformation et fonction publiques | 148, 348, 349, 368 |
| VA | Cohésion des territoires | 109, 112, 135, 147, 162, 177 |

### BA — Budgets annexes (2 missions, 5 programmes)

| Code | Mission | Programmes |
|------|---------|------------|
| XC | Contrôle et exploitation aériens | 612, 613, 614 |
| XJ | Publications officielles et information administrative | 623, 624 |

### CAS — Comptes d'affectation spéciale (6 missions, 15 programmes)

| Code | Mission | Programmes |
|------|---------|------------|
| YB | Gestion du patrimoine immobilier de l'État | 721, 723 |
| YC | Participations financières de l'État | 731, 732 |
| YD | Pensions | 741, 742, 743 |
| YE | Contrôle de la circulation et du stationnement routiers | 751, 753, 754, 755 |
| YF | Développement agricole et rural | 775, 776 |
| YK | Financement des aides aux collectivités pour l'électrification rurale | 793, 794 |

### CCF — Comptes de concours financiers (4 missions, 21 programmes)

| Code | Mission | Programmes |
|------|---------|------------|
| ZB | Avances à divers services de l'État | 821, 823, 824, 825, 826, 827, 828, 830 |
| ZC | Avances aux collectivités territoriales | 832, 833, 834 |
| ZE | Prêts à des États étrangers | 851, 852, 853, 854 |
| ZF | Prêts et avances à des particuliers ou organismes privés | 861, 862, 869, 876, 877, 878 |

## Contenu des PDFs

### Document MSN (mission)
Page de couverture → Note explicative (base LOLF art. 51-5) → Récapitulatif des crédits par destination/nature → Programmation stratégique → Descriptif des réformes → Puis, pour chaque programme : indicateurs de performance, justification au premier euro, opérateurs.

### Document PGM (programme)
Page de couverture → Présentation stratégique du programme → Responsable du programme → Objectifs et indicateurs de performance → Justification au premier euro → Opérateurs (le cas échéant).
