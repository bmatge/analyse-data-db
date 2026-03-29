# Bibliothèque de datavisualisations

## Principes

Trois niveaux d'autonomie pour les dataviz :

| Niveau | Pages | Mise à jour | Modifiable |
|--------|-------|-------------|------------|
| **Figées** | Budget de l'État, Performance | Import Tango/2PERF automatique | Non (modèle fixe) |
| **Semi-figées** | Panorama FP, Budget annuel, SMB | Manuelle (données tabulaires) | Oui (ajout/retrait de blocs) |
| **À la carte** | Repères, articles | Manuelle | Oui (choix libre dans la bibliothèque) |

## Types de dataviz disponibles

### Dans la bibliothèque (réutilisables)

| Type | Usage principal | Colonnes par défaut |
|------|----------------|---------------------|
| **Chiffres clés** | Exergues sur toutes les sections | 4 ou 6 |
| **Polar Chart** | Panorama FP | 6 |
| **Line Chart** | Panorama FP, Performance | 6 |
| **Area Chart** | Panorama FP | 6 |
| **Double Area Chart** | Suivi mensuel budget | 6 |
| **Line-Area Chart** | Suivi mensuel budget (écarts) | 6 |
| **Histogramme classique** | Panorama FP | 12 |
| **Histogramme sur 100%** | Panorama FP | 6 |
| **Stacked Histogramme** | Panorama FP | 12 |
| **Stacked Histogramme 100%** | Panorama FP | 6 |
| **Grouped Histogramme** | Panorama FP (comparaisons) | 12 |
| **Dot Plot** | Performance (sous-indicateurs) | 12 |
| **Cartographie** | Panorama FP (Europe) | 6 |

### Hors bibliothèque (modèles ad-hoc)

| Type | Usage |
|------|-------|
| **Bar Chart classique** | Budget de l'État (par type budget) |
| **Bar Chart sur 100%** | Budget de l'État |
| **Tree Map** (bar chart à largeur fixe) | Budget annuel (recettes/dépenses/solde) |
| **Stacked Bar Chart** | Budget de l'État |
| **Clustered Force Layout** (bulles) | Budget annuel (recettes fiscales, dépenses missions) |

## Structure d'un bloc dataviz

Chaque bloc comporte :
- Titre
- Représentation graphique (type choisi)
- Données (tabulaires)
- Couleurs (palette choisie)
- Légende
- Unité (ex : "en milliards d'€")
- Source
- Tooltip (facultatif)
- Texte de contexte (facultatif)

## Indicateurs par section

### Budget annuel
- Recettes / Dépenses / Solde du budget prévisionnel → Tree Map
- Focus budget général (recettes fiscales détaillées, dépenses missions) → Clustered Force Layout
- Focus budgets annexes et comptes spéciaux → Clustered Force Layout + Tree Map

### Suivi mensuel du budget (SMB)
- Chiffres clés mensuels (recettes fiscales, non fiscales, dépenses, solde)
- Cumul annuel → Double Area Chart
- Écarts N/N-1 → Line-Area Chart
- Navigation par année + mois + indicateur (recettes/dépenses/solde)

### Dépenses par ministère / par mission
- AE et CP par niveau (mission → programme → action)
- ETPT par niveau (mission → programme)
- 4 types de budget × 3 exercices
- Dataviz interactives avec drill-down

### Dépenses par nature
- Ventilation par Titre > Catégorie
- AE et CP

### Performance de la dépense
- Synthèse : Dot Plot (billes par degré de réalisation)
- Par mission : histogrammes empilés
- Par programme : Line Chart (réalisations passées + cible)
- Détail sous-indicateur : courbe avec projection

### Panorama des finances publiques
- Vue d'ensemble (État, APUL, ASSO)
- État & ODAC
- APUL (collectivités)
- ASSO (sécurité sociale)
- Comparaison européenne
