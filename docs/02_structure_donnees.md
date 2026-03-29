# Structure des données budgétaires

## Sources de données

Les données budgétaires proviennent de 3 systèmes d'export :

| Système | Données | Fréquence |
|---------|---------|-----------|
| **Tango** (via Farandole) | Budget (AE/CP), ETPT, Dépenses par nature | À chaque loi de finances |
| **2BOO** | Opérateurs | Annuel (PLR uniquement) |
| **2PERF** | Performance de la dépense | Annuel (PLR uniquement) |

## Les 5 jeux de données

### 1. Données du budget (AE / CP)

- **Budgets** : BG, BA, CAS, CCF
- **Exercices** : PLF, LFI, PLR (1 fichier par exercice)
- **Granularité** : Mission > Programme > Action > Sous-action
- **Colonnes** :
  - Année
  - Type de budget
  - Code Mission / Mission
  - Code Programme / Programme
  - Code Action / Action
  - Code Sous-Action / Sous-Action
  - **AE** (Autorisations d'Engagement)
  - **CP** (Crédits de Paiement)
  - Code Ministère / Ministère
  - Commentaires quali Ministère / Mission / Programme

### 2. Données ETPT

- **Budgets** : BG, BA, CAS, CCF
- **Exercices** : PLF, LFI, PLR
- **Granularité** : Mission > Programme (pas d'action)
- **Colonnes** :
  - Année, Type de budget
  - Code Ministère / Ministère
  - Code Mission / Mission
  - Code Programme / Programme
  - **ETPT** (Équivalent Temps Plein Travaillé)
  - Commentaires quali Ministère / Mission / Programme

### 3. Données par nature

- **Budgets** : BG, CAS, CCF (pas de BA)
- **Exercices** : PLF, LFI, PLR
- **Granularité** : Titre > Catégorie
- **Colonnes** :
  - Année, Type de budget
  - Code Mission / Mission
  - Code Programme / Programme
  - Code Action / Action
  - Code Sous-Action / Sous-Action
  - Code Catégorie / Catégorie
  - AE, CP
  - Code Titre / Titre
  - Code Ministère / Ministère
  - Commentaires quali Titre

### 4. Données opérateurs

- **Budget** : BG uniquement
- **Exercice** : PLR uniquement
- **Source** : Bureau 2BOO
- **Colonnes** :
  - Code Mission / Mission
  - Code Programme / Programme
  - Code Ministère / Ministère
  - **Opérateur**
  - CR Produits : SCSP, Crédits d'intervention, Fiscalité affectée, Autres subventions, Autres produits, Total
  - Total financement public
  - Ratio financement public / Produits Total
  - ETPT autres emplois, ETPT rémunérés, Emplois totaux
  - Commentaires quali Ministère / Mission / Programme

### 5. Données performance

- **Budgets** : BG, BA, CAS, CCF
- **Exercice** : PLR uniquement
- **Source** : Bureau 2PERF
- **Granularité** : Mission > Programme > Objectif > Indicateur > Sous-indicateur
- **Colonnes** :
  - Année, Type de budget
  - Code Mission / Mission
  - Code Programme / Programme
  - Identifiant Objectif / Numéro / Libellé
  - Identifiant Indicateur / Numéro / Libellé / Type
  - Stratégie niveau mission
  - Identifiant sous-indicateur / Libellé / Unité
  - **Réalisation N-2, N-1, N PAR N**
  - **Prévision N PAP N+1**
  - **Réalisation N**
  - **Année cible / Valeur cible**
  - **Degré de réalisation** (Cible atteinte / Amélioration / Absence d'amélioration / Données non renseignées / Données non retenues)
  - Code Ministère / Ministère
  - Commentaires quali des sous-indicateurs

## Règles d'import et d'écrasement

- Les données **ne s'écrasent pas d'une année sur l'autre** ni d'une loi de finances à l'autre
- PLF 2019 n'écrase pas PLF 2018 ; LFI 2019 n'écrase pas PLF 2019
- Seule une **nouvelle version du même exercice de la même année** écrase l'ancienne
- Les fichiers par exercice arrivent séquentiellement au cours de l'année (PLF → LFI → PLR)

## Structure d'URL canonique des données

```
/budget-etat/annee/{annee}/exercice/{PLF|LFI|PLR}/ministeres
/budget-etat/annee/{annee}/exercice/{PLF|LFI|PLR}/ministere/{code_ministere}
/budget-etat/annee/{annee}/exercice/{PLF|LFI|PLR}/ministere/{code_ministere}/mission/{code_mission}
/budget-etat/annee/{annee}/exercice/{PLF|LFI|PLR}/ministere/{code_ministere}/mission/{code_mission}/programme/{code_programme}
/budget-etat/annee/{annee}/exercice/{PLF|LFI|PLR}/missions
/budget-etat/annee/{annee}/exercice/{PLF|LFI|PLR}/mission/{code_mission}
/budget-etat/annee/{annee}/exercice/{PLF|LFI|PLR}/mission/{code_mission}/programme/{code_programme}
/budget-etat/annee/{annee}/exercice/{PLF|LFI|PLR}/programmes
/budget-etat/annee/{annee}/exercice/{PLF|LFI|PLR}/nature
/budget-etat/annee/{annee}/exercice/{PLF|LFI|PLR}/nature/titre/{code_titre}
/budget-etat/annee/{annee}/exercice/{PLF|LFI|PLR}/nature/titre/{code_titre}/categorie/{code_categorie}
/budget-etat/annee/{annee}/exercice/{PLF|LFI|PLR}/operateurs

/donnees-performance/annee/{annee}/missions
/donnees-performance/annee/{annee}/mission/{code_mission}
/donnees-performance/annee/{annee}/mission/{code_mission}/programme/{code_programme}
/donnees-performance/annee/{annee}/programmes
/donnees-performance/annee/{annee}/programme/{code_programme}
```
