# Plan de classement documentaire

## Principe

Les documents budgétaires suivent **la même arborescence** que les données. La nomenclature (Mission, Programme) est la clé de liaison entre données et documentation.

## Arborescence cible

```
Documents budgétaires
└── Exercice {année}
    └── Budget Annuel
        └── {Loi de finances} (PLF / LFI / PLR / LFR / PLFR)
            └── {Type de document} (PAP = bleu de LFI, RAP, etc.)
                └── Missions du {type budget} (BG / BA / CAS / CCF)
                    └── {Nom de la mission}
                        └── {Code programme} - {Nom du programme}.pdf
```

## Types de documents budgétaires

| Sigle | Nom complet | Moment |
|-------|-------------|--------|
| **PAP** | Projet Annuel de Performances | PLF (accompagne le projet de loi) |
| **RAP** | Rapport Annuel de Performances | PLR (accompagne le règlement) |
| **DPT** | Document de Politique Transversale | PLF |
| **Jaune** | Annexe "jaune" budgétaire | PLF |
| **Circulaire** | Circulaire budgétaire | Variable |
| **Décret** | Décret budgétaire | Variable |

## Niveaux de documents

Deux niveaux de granularité existent dans les documents :

### Niveau Mission (MSN)
- Vue d'ensemble de la mission : note explicative, crédits par destination/nature, programmation stratégique
- Contient un résumé de tous les programmes de la mission

### Niveau Programme (PGM)
- Détail d'un programme : présentation stratégique, objectifs, indicateurs de performance, justification au premier euro, opérateurs
- Document autonome, rattaché à une mission

## Filtres de recherche documentaire (facettes)

La documentation est filtrable selon 6 axes :

| Filtre | Source | Exemple de valeurs |
|--------|--------|--------------------|
| **Exercice** | Année | 2025, 2024, 2023... |
| **Typologie** | Tag | RAP, PAP, DPT, jaune, circulaire, décret... |
| **Loi de finances** | Tag | PLF, LFI, PLR, LFR, PLFR... |
| **Ministère** | Nomenclature | Liste des 17 ministères |
| **Mission** | Nomenclature | Liste des 49 missions |
| **Programme** | Nomenclature | Liste des 190 programmes |
| **Institution** | Tag | Assemblée nationale, Cour des comptes... |

Le facetting est essentiel : si un filtre ne contient aucun résultat pour la sélection courante, il ne s'affiche pas.

## Liaison document ↔ données

Un document est automatiquement associé aux URLs de données correspondantes.

Exemple : `DBGPGMLFIPGM104.pdf` (lire D-BG-PGM-LFI-PGM-104) est lié à :
```
/budget-etat/annee/2019/exercice/LFI/ministere/09/mission/IA/programme/104
/budget-etat/annee/2019/exercice/LFI/mission/IA/programme/104
/budget-etat/annee/2019/exercice/LFI/programme/104
/donnees-performance/annee/2019/mission/IA/programme/104
/donnees-performance/annee/2019/programme/104
```

La correspondance entre le code programme (104) et la mission (IA) + le ministère (09) vient de la **nomenclature** de l'année concernée.
