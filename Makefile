PYTHON = python3
CLI = $(PYTHON) -m src.cli
DB = db/budget.db

.PHONY: init load load-documents reconcile validate load-all clean serve

## Initialiser la base de données et charger les constantes
init:
	$(CLI) init

## Charger les données CSV pour une année : make load YEAR=2025
load:
	$(CLI) load $(YEAR)

## Scanner et indexer les documents PDF : make load-documents YEAR=2025
load-documents:
	$(CLI) load-documents $(YEAR)

## Construire les entités canoniques pour le suivi inter-annuel
reconcile:
	$(CLI) reconcile

## Lancer les vérifications : make validate YEAR=2025
validate:
	$(CLI) validate $(YEAR)

## Pipeline complet pour une année : make load-all YEAR=2025
load-all:
	$(CLI) load-all $(YEAR)

## Charger les 3 jeux de données open data + documents + réconciliation
load-all-years: init
	$(CLI) load 2014
	$(CLI) load 2024
	$(CLI) load 2025
	$(CLI) load-documents 2025
	$(CLI) reconcile
	$(CLI) validate 2014
	$(CLI) validate 2024
	$(CLI) validate 2025

## Lancer le serveur web
serve:
	$(PYTHON) -m uvicorn src.web.app:app --reload --port 8000

## Supprimer la base de données
clean:
	rm -f $(DB)

## Aide
help:
	@echo "Commandes disponibles :"
	@echo "  make init              - Initialiser la base"
	@echo "  make load YEAR=2025    - Charger les données CSV"
	@echo "  make load-documents YEAR=2025 - Indexer les PDFs"
	@echo "  make reconcile         - Entités canoniques"
	@echo "  make validate YEAR=2025 - Vérifications"
	@echo "  make load-all YEAR=2025 - Pipeline complet"
	@echo "  make load-all-years    - Charger 2014+2024+2025"
	@echo "  make serve             - Lancer le serveur web"
	@echo "  make clean             - Supprimer la base"
