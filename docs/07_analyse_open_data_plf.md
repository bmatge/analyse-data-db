# Analyse comparative des PLF Open Data (2014, 2024, 2025)

## Sources

| Fichier | Année | Lignes | Colonnes | Contenu |
|---------|-------|--------|----------|---------|
| `plf-2014-nomenclature-par-destination.csv` | 2014 | 722 | 7 | Nomenclature seule (pas de montants) |
| `plf-2024-depenses-2024-selon-nomenclatures-destination-et-nature.csv` | 2024 | 2 392 | 16 | Nomenclature + dépenses (AE/CP) + nature |
| `plf25-depenses-2025-du-bg-et-des-ba-selon-nomenclatures-destination-et-nature.csv` | 2025 | 2 415 | 16 | Idem 2024 |

Encodage : UTF-8 avec BOM, séparateur `;`

## Évolution du schéma

### PLF 2014 — Nomenclature pure

```
Phase ; Type de Mission ; Mission ; Code Programme ; Programme ; Code Action ; Action
```

- Granularité maximale : Action (pas de sous-action)
- Pas de montants financiers
- Pas de code mission
- Pas de ministère
- Types de budget en texte complet ("Budget général", "Budgets annexes"...)

### PLF 2024 & 2025 — Nomenclature + Dépenses + Nature

```
Type Mission ; Mission ; Code Mission ; Programme ; Libellé Programme ;
Action ; Libellé Action ; Sous Action ; Libellé SousAction ;
Catégorie ; Code Titre ;
AE PLF ; CP PLF ; AE Prev FDC/ADP ; CP Prev FDC/ADP ;
Ministère
```

- Granularité maximale : Sous-action × Catégorie (croisement destination + nature)
- Montants financiers : AE et CP (PLF + prévisions FDC/ADP)
- Code mission 2 lettres ajouté
- Ministère ajouté
- Types de budget abrégés (BG, BA, CAS, CCF)
- ~3× plus de lignes grâce au croisement destination × nature

**Le schéma 2024 et 2025 est strictement identique** (16 colonnes, mêmes noms).

### Correspondance des colonnes

| 2014 | 2024/2025 | Changement |
|------|-----------|------------|
| `Phase` | — | Supprimé |
| `Type de Mission` | `Type Mission` | Renommé + abrégé (BG/BA/CAS/CCF) |
| `Mission` | `Mission` | Stable |
| — | `Code Mission` | **Ajouté** (2 lettres) |
| `Code Programme` | `Programme` | Renommé, int→float |
| `Programme` | `Libellé Programme` | Renommé |
| `Code Action` | `Action` | Renommé |
| `Action` | `Libellé Action` | Renommé |
| — | `Sous Action` / `Libellé SousAction` | **Ajouté** (76% nulls) |
| — | `Catégorie` | **Ajouté** (code 10-73) |
| — | `Code Titre` | **Ajouté** (1-7) |
| — | `AE PLF` / `CP PLF` | **Ajouté** |
| — | `AE Prev FDC/ADP` / `CP Prev FDC/ADP` | **Ajouté** |
| — | `Ministère` | **Ajouté** |

## Éléments CONSTANTS (stables dans le temps)

### La hiérarchie budgétaire
La structure Mission → Programme → Action (→ Sous-action) est **invariante**. C'est le squelette permanent du budget.

### Les 4 types de budget
BG, BA, CAS, CCF sont présents dans les 3 années. Les deux types supplémentaires (CCO, COM) n'apparaissent pas dans l'open data (cohérent : ils n'ont pas de crédits votés au même sens).

### 35 missions stables sur 10 ans (2014→2025)
Action extérieure de l'État, Administration générale et territoriale de l'État, Agriculture alimentation forêt et affaires rurales, Aide publique au développement, Conseil et contrôle de l'État, Contrôle de la circulation et du stationnement routiers, Contrôle et exploitation aériens, Culture, Défense, Développement agricole et rural, Direction de l'action du Gouvernement, Écologie développement et mobilité durables, Économie, Engagements financiers de l'État, Enseignement scolaire, Financement des aides aux collectivités pour l'électrification rurale, Gestion du patrimoine immobilier de l'État, Immigration asile et intégration, Justice, Médias livre et industries culturelles, Outre-mer, Participations financières de l'État, Pensions, Pouvoirs publics, Prêts à des États étrangers, Prêts et avances à des particuliers ou à des organismes privés, Publications officielles et information administrative, Recherche et enseignement supérieur, Relations avec les collectivités territoriales, Régimes sociaux et de retraite, Remboursements et dégrèvements, Santé, Sécurités, Solidarité insertion et égalité des chances, Sport jeunesse et vie associative.

### 133 codes programme stables (2014→2025)
Noyau dur de programmes identifiés par le même code numérique sur 10 ans. Le code programme est l'identifiant le plus fiable pour le suivi longitudinal.

### Les 7 titres et 19 catégories de dépenses
Structure de la nomenclature par nature, invariante.

## Éléments VARIABLES

### Noms de ministères — très instables
Les noms changent à **chaque remaniement gouvernemental**. Sur 2024→2025 seulement :
- Seulement **5 noms identiques** (Culture, Enseignement supérieur, Europe et affaires étrangères, Justice, Services du Premier ministre)
- 12 noms uniquement 2024, 15 uniquement 2025

Exemples :
| 2024 | 2025 |
|------|------|
| Armées | Armées et anciens combattants |
| Intérieur et outre-mer | Intérieur (séparé de Outre-mer) |
| Économie, finances et souveraineté industrielle et numérique | Économie, finances et industrie |
| Transition écologique et cohésion des territoires | Transition écologique, énergie, climat et prévention des risques |

**Conséquence : ne jamais utiliser le nom de ministère comme clé stable. Utiliser le code ministère de la nomenclature.**

### Missions — relativement stables, mais évolutions notables

**13 missions supprimées entre 2014 et 2024** (fusions, restructurations) :
- Gestion des FP et des ressources humaines → scindée en "Gestion des FP" + "Transformation et fonction publiques"
- Provisions → renommée "Crédits non répartis"
- Égalité des territoires, logement et ville → absorbée
- Politique des territoires → absorbée dans "Cohésion des territoires"
- Plusieurs CAS disparus (Accords monétaires, Spectre hertzien, Grèce...)

**Évolutions 2024→2025** (3 missions renommées) :
| 2024 | 2025 |
|------|------|
| Avances à l'audiovisuel public (CAS ZD) | Audiovisuel public (BG AQ) — changé de type budget ! |
| Avances aux collectivités territoriales | ...et aux collectivités régies par les art. 73, 74 et 76 |
| Travail et emploi | Travail, emploi et administration des ministères sociaux |

Le passage de l'audiovisuel public de CAS à BG en 2025 est un cas remarquable de **changement de type de budget** pour une mission.

### Programmes — noyau stable + renouvellement

| | 2014 | 2024 | 2025 |
|---|---|---|---|
| Total programmes | 196 | 170 | 167 |
| Stables depuis 2014 | — | 133 | 133 |
| Supprimés depuis 2014 | — | 57 | 57 |
| Nouveaux depuis 2014 | — | ~30 | ~30 |

**57 programmes supprimés** depuis 2014 :
- Série 400 (PIA "investissements d'avenir" 1ère génération : P401-P414)
- Programmes CAS restructurés (P752, P761-763, P785-789, P791-796, P811-813, etc.)
- Fusions de programmes (P106, P115, P154, P167, P168, P170...)

**22 programmes renommés** (même code, libellé modifié) — exemples :
| Code | 2014 | 2024/2025 |
|------|------|-----------|
| 149 | Forêt | Compétitivité et durabilité de l'agriculture, de l'agroalimentaire et de la forêt |
| 177 | Prévention de l'exclusion... | Hébergement, parcours vers le logement... |
| 224 | Transmission des savoirs et démocratisation de la culture | Soutien aux politiques du ministère de la culture |
| 304 | Lutte contre la pauvreté : RSA... | Inclusion sociale et protection des personnes |
| 751 | Radars | Structures et dispositifs de sécurité routière |

**Programmes nouveaux en 2025** (audiovisuel public basculé de CAS vers BG) :
- P372 (France Télévisions), P373 (ARTE), P374 (Radio France), P375 (France Médias Monde), P376 (INA), P377 (TV5 Monde), P383, P384

### Schéma des fichiers open data — en évolution

Le format a radicalement changé entre 2014 et 2024 :
- 2014 : nomenclature pure, 7 colonnes, granularité Action
- 2024+ : nomenclature + données, 16 colonnes, granularité Sous-action × Catégorie

Même entre 2024 et 2025, la convention de nommage des fichiers n'est pas identique (`plf-2024-...` vs `plf25-...`).

## Enseignements pour le projet

1. **Le code programme est la meilleure clé de suivi longitudinal** — 68% des codes de 2014 sont encore actifs en 2025
2. **Le nom de ministère ne doit jamais être une clé** — il change à chaque gouvernement
3. **Le code mission est fiable à moyen terme** mais peut changer (ex: audiovisuel public ZD→AQ en 2025)
4. **Tout système de classement doit être versionné par année** — la nomenclature est contextuelle
5. **Le schéma open data s'est stabilisé** entre 2024 et 2025, mais n'est pas garanti pour les années futures
6. **Les sous-actions sont souvent absentes** (~75% de nulls) — la granularité fiable s'arrête à l'Action
