#!/usr/bin/env bash
set -euo pipefail

COMPOSE="docker compose -f docker-compose.yml -f docker-compose.prod.yml"
APP="budget-explorer"

# Full pipeline: load all years 2023-2026 with nomenclature, credits, and documents
run_pipeline() {
  local EXEC="${1:-docker exec $APP}"

  echo "--- Init DB ---"
  $EXEC python3 -m src.cli init

  echo "--- 2023 PLRG ---"
  $EXEC python3 -m src.cli load-nomenclature 2023 --exercice plr
  $EXEC python3 -m src.cli load-xls 2023 --exercice PLR
  $EXEC python3 -m src.cli load-documents 2023 --exercice PLR

  echo "--- 2024 PLF ---"
  $EXEC python3 -m src.cli load-nomenclature 2024 --exercice plf
  $EXEC python3 -m src.cli load 2024
  $EXEC python3 -m src.cli load-documents 2024 --exercice PLF

  echo "--- 2024 PLRG ---"
  $EXEC python3 -m src.cli load-nomenclature 2024 --exercice plr
  $EXEC python3 -m src.cli load-xls 2024 --exercice PLR
  $EXEC python3 -m src.cli load-documents 2024 --exercice PLR

  echo "--- 2025 PLF ---"
  $EXEC python3 -m src.cli load-nomenclature 2025 --exercice plf
  $EXEC python3 -m src.cli load 2025
  $EXEC python3 -m src.cli load-documents 2025 --exercice PLF

  echo "--- 2026 PLF ---"
  $EXEC python3 -m src.cli load-nomenclature 2026 --exercice plf
  $EXEC python3 -m src.cli load-xls 2026 --exercice PLF
  $EXEC python3 -m src.cli load-documents 2026 --exercice PLF

  echo "--- Reconciliation ---"
  $EXEC python3 -m src.cli reconcile

  echo "--- Validation ---"
  $EXEC python3 -m src.cli validate 2023
  $EXEC python3 -m src.cli validate 2024
  $EXEC python3 -m src.cli validate 2025
  $EXEC python3 -m src.cli validate 2026

  echo "--- Sankey data ---"
  $EXEC python3 -m src.export_sankey_data
  $EXEC python3 -m src.export_sankey_plf_plrg
}

case "${1:-deploy}" in

  init)
    echo "=== Initialisation complète ==="
    git pull --ff-only
    $COMPOSE build
    $COMPOSE up -d
    docker exec "$APP" rm -f /app/db/budget.db
    run_pipeline
    echo "=== Init terminée ==="
    ;;

  deploy)
    echo "=== Mise à jour ==="
    $COMPOSE down
    git pull --ff-only
    $COMPOSE build
    $COMPOSE up -d --remove-orphans
    docker image prune -f
    echo "=== Déployé ==="
    ;;

  build-pipeline)
    echo "=== Construction de la pipeline ==="
    docker exec "$APP" rm -f /app/db/budget.db
    run_pipeline
    echo "=== Pipeline terminée ==="
    ;;

  reload-data)
    echo "=== Rechargement des données ==="
    docker exec "$APP" rm -f /app/db/budget.db
    run_pipeline
    echo "=== Données rechargées ==="
    ;;

  stop)
    $COMPOSE down
    ;;

  logs)
    $COMPOSE logs -f
    ;;

  status)
    $COMPOSE ps
    ;;

  *)
    echo "Usage: $0 {init|deploy|build-pipeline|reload-data|stop|logs|status}"
    echo ""
    echo "  init            Pull, build, start, load all data"
    echo "  deploy          Pull, rebuild, restart (no data reload)"
    echo "  build-pipeline  Rebuild DB from scratch (2023-2026)"
    echo "  reload-data     Alias for build-pipeline"
    echo "  stop            Stop containers"
    echo "  logs            Follow container logs"
    echo "  status          Show container status"
    exit 1
    ;;
esac
