# Modèle de liaison Data ↔ Documentation

## Le problème

Les données budgétaires (chiffres AE/CP, ETPT, performance) et les documents (PAP, RAP, DPT...) vivent dans deux mondes séparés mais partagent **la même structure hiérarchique**. L'objectif est de les relier pour permettre :

1. Depuis une dataviz → accéder au document source
2. Depuis un document → voir les données associées
3. Navigation transversale par nomenclature

## La clé de liaison : la nomenclature

```
         NOMENCLATURE (année N)
              │
    ┌─────────┼─────────┐
    │         │         │
  DONNÉES   DOCUMENTS  PERFORMANCE
  (Tango)   (PAP/RAP)  (2PERF)
```

Toute entité (mission, programme, action) est identifiable par le triplet :
```
(année, type_budget, code)
```

## Schéma relationnel simplifié

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   MINISTERE  │     │   MISSION    │     │  TYPE_BUDGET  │
│──────────────│     │──────────────│     │──────────────│
│ code (num)   │     │ code (2 let) │     │ code (BG/BA/ │
│ libelle      │     │ libelle      │     │  CAS/CCF)    │
│ année        │     │ type_budget  │     └──────┬───────┘
└──────┬───────┘     │ année        │            │
       │             └──────┬───────┘            │
       │                    │                    │
       └────────┬───────────┘                    │
                │                                │
         ┌──────┴───────┐                        │
         │  PROGRAMME   │────────────────────────┘
         │──────────────│
         │ code (3 ch)  │
         │ libelle      │
         │ mission_code │
         │ ministere_code│
         │ année        │
         └──────┬───────┘
                │
    ┌───────────┼───────────┐
    │           │           │
┌───┴───┐ ┌────┴────┐ ┌────┴────┐
│ACTION │ │DOCUMENT │ │ DONNEE  │
│───────│ │─────────│ │─────────│
│code   │ │fichier  │ │ AE/CP   │
│libelle│ │type_doc │ │ ETPT    │
│       │ │exercice │ │ exercice│
└───┬───┘ │année    │ │ année   │
    │     │loi_fin  │ └─────────┘
┌───┴───┐ └─────────┘
│SS-ACT │
│───────│
│code   │
│libelle│
└───────┘
```

## Identifiant unique d'un document

Pour positionner un document dans le plan de classement, il faut extraire de son nom/chemin :

| Attribut | Source (PLF 2025) | Exemple |
|----------|-------------------|---------|
| Année | Répertoire parent ou nom | `2025` |
| Exercice / Loi de finances | Nom fichier (`PLF`) | `PLF` |
| Type de document | Préfixe (`PAP`) | `PAP` |
| Type de budget | Répertoire niveau 1 | `BG` |
| Code mission | Répertoire MSN ou nom PGM | `DA` |
| Code programme | Répertoire PGM ou nom | `178` |

### Extraction depuis les conventions de nommage actuelles

**Fichier MSN** : `PAP2025_BG_Defense_DA.pdf`
```
type_doc  = PAP
année     = 2025
budget    = BG
mission   = DA
programme = (tous les programmes de la mission)
```

**Fichier PGM** : `FR_2025_PLF_DA_PGM_178.pdf`
```
année     = 2025
exercice  = PLF
mission   = DA
programme = 178
```

## Associations automatiques

À partir d'un document programme (ex: programme 178, mission DA, PLF 2025), on peut automatiquement :

1. **Lier aux données budget** : AE/CP du programme 178 pour PLF 2025
2. **Lier aux données ETPT** : effectifs du programme 178 pour PLF 2025
3. **Lier aux données par nature** : ventilation titre/catégorie du programme 178
4. **Lier à la performance** : indicateurs du programme 178 (si PLR)
5. **Lier au document mission** : PAP de la mission DA
6. **Lier aux documents frères** : autres programmes de la mission DA (144, 146, 212)
7. **Lier au ministère** : via la nomenclature, programme 178 → ministère X

## Dimensions de navigation

```
                    PAR ANNÉE
                   2023 │ 2024 │ 2025
                        │      │
    PAR LOI DE FINANCES ─┼──────┼── PLF / LFI / PLR
                        │      │
    PAR TYPE BUDGET ────┼──────┼── BG / BA / CAS / CCF
                        │      │
    PAR MINISTÈRE ──────┼──────┼── 17 ministères
                        │      │
    PAR MISSION ────────┼──────┼── 49 missions
                        │      │
    PAR PROGRAMME ──────┼──────┼── 190 programmes
                        │      │
    PAR TYPE DOC ───────┼──────┼── PAP / RAP / DPT / Jaune / Circulaire...
                        │      │
    PAR NATURE ─────────┼──────┼── 7 titres > 19 catégories
```

Chaque dimension est un axe de filtre pour la recherche et la dataviz.
