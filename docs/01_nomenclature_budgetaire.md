# Nomenclature budgétaire

## Source

Fichier : `entrants/documentation/Nomenclature_0510_10h(3).xls`
Dernière mise à jour connue : 2021-10-05 (Sylvie Mocchi)
Export CSV complet : `entrants/documentation/Nomenclature_0510_FULL_DUMP.csv`

## Structure du fichier

Feuille unique `Nomenclature` — 2 562 lignes de données, 8 colonnes :

| Colonne | Nom | Description |
|---------|-----|-------------|
| A | `Type ligne` | Code hiérarchique (TTR, CAT, MIN, MSN, PGM, ACT, SSA) |
| B | `Type Budget` | BG, BA, CAS, CCF |
| C | `code` | Identifiant (format variable selon le type) |
| D | `Mission` | Code mission 2 lettres (renseigné sur les lignes PGM) |
| E | `Ministere` | Code ministère numérique (renseigné sur les lignes PGM) |
| F | `Libelle` | Libellé complet |
| G | `Libelle abrege` | Libellé abrégé |
| H | `commentFP` | Commentaire (221 lignes renseignées) |

## Hiérarchie des entités

```
TTR  Titre (7)                    code numérique 1-7
 └─ CAT  Catégorie (19)           code numérique 10-73
MIN  Ministère (17)               code numérique 1-70
MSN  Mission (49)                 code 2 lettres (AA-ZF)
 └─ PGM  Programme (190)          code 3 chiffres (101-878)
     └─ ACT  Action (804)         code PGM-NN (ex: 105-01)
         └─ SSA  Sous-action (1476)  code PGM-NN-NN (ex: 105-01-01)
```

## Relations clés

- **PGM → MSN** : chaque ligne PGM porte le code mission (colonne D)
- **PGM → MIN** : chaque ligne PGM porte le code ministère (colonne E)
- **ACT → PGM** : le code action est préfixé par le numéro de programme
- **SSA → ACT** : le code sous-action est préfixé par le code action

Les missions (MSN) et ministères (MIN) ne sont pas directement liés entre eux dans la nomenclature. C'est le programme qui fait le pont.

## Titres de dépenses (TTR)

| Code | Libellé |
|------|---------|
| 1 | Dépenses de personnel |
| 2 | Dépenses de fonctionnement |
| 3 | Dépenses d'investissement |
| 4 | Dépenses d'intervention (hors transferts financiers) |
| 5 | Dépenses d'intervention (transferts financiers) |
| 6 | Dépenses d'opérations financières |
| 7 | Dépenses d'opérations financières (dotation en fonds propres) |

## Convention des codes mission par type de budget

La première lettre du code mission encode le type de budget :

| Première lettre | Type de budget |
|-----------------|---------------|
| A - V | BG (Budget général) |
| X | BA (Budgets annexes) |
| Y | CAS (Comptes d'affectation spéciale) |
| Z | CCF (Comptes de concours financiers) |

## Plages de numéros de programme par type de budget

| Type | Plage |
|------|-------|
| BG | 101 - 552 |
| BA | 612 - 624 |
| CAS | 721 - 794 |
| CCF | 821 - 878 |

## Point d'attention

**Les codes sont contextuels par année.** Le programme 104 en 2019 peut ne pas correspondre au même programme 104 en 2018. Il faut toujours associer les données à la nomenclature de l'année correspondante.
