#!/usr/bin/env bash
set -euo pipefail

COMPOSE="docker compose -f docker-compose.yml -f docker-compose.prod.yml"
APP="budget-explorer"

case "${1:-deploy}" in

  init)
    echo "=== Initialisation complète ==="
    git pull --ff-only
    $COMPOSE build
    $COMPOSE up -d
    echo "--- Chargement des données ---"
    docker exec "$APP" python3 -m src.cli init
    docker exec "$APP" python3 -m src.cli load 2014
    docker exec "$APP" python3 -m src.cli load 2024
    docker exec "$APP" python3 -m src.cli load 2025
    docker exec "$APP" python3 -m src.cli load-documents 2025
    docker exec "$APP" python3 -m src.cli reconcile
    docker exec "$APP" python3 -m src.cli validate 2014
    docker exec "$APP" python3 -m src.cli validate 2024
    docker exec "$APP" python3 -m src.cli validate 2025
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

  reload-data)
    echo "=== Rechargement des données ==="
    docker exec "$APP" rm -f /app/db/budget.db
    docker exec "$APP" python3 -m src.cli init
    docker exec "$APP" python3 -m src.cli load 2014
    docker exec "$APP" python3 -m src.cli load 2024
    docker exec "$APP" python3 -m src.cli load 2025
    docker exec "$APP" python3 -m src.cli load-documents 2025
    docker exec "$APP" python3 -m src.cli reconcile
    docker exec "$APP" python3 -m src.cli validate 2014
    docker exec "$APP" python3 -m src.cli validate 2024
    docker exec "$APP" python3 -m src.cli validate 2025
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
    echo "Usage: $0 {init|deploy|reload-data|stop|logs|status}"
    exit 1
    ;;
esac
