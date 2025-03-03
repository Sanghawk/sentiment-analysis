#!/usr/bin/env bash

# "refresh_api.sh" - a script to rebuild and restart the 'api' service using docker compose.
# Supports optional "no-cache" build and log-following.
#
# Usage examples:
#   ./refresh_api.sh               -> normal rebuild + start
#   ./refresh_api.sh no-cache      -> no-cache rebuild + start
#   ./refresh_api.sh logs          -> normal rebuild + start, then follow logs
#   ./refresh_api.sh no-cache logs -> no-cache rebuild + start, then follow logs

API_SERVICE_NAME="api"

# Default flags
NO_CACHE=false
FOLLOW_LOGS=false

# Parse arguments
for arg in "$@"; do
  case "$arg" in
    no-cache)
      NO_CACHE=true
      ;;
    logs)
      FOLLOW_LOGS=true
      ;;
  esac
done

# Step 1: Build the 'api' service
if [ "$NO_CACHE" = true ]; then
  echo "[refresh_api] Building '$API_SERVICE_NAME' with --no-cache..."
  docker compose build --no-cache "$API_SERVICE_NAME"
else
  echo "[refresh_api] Building '$API_SERVICE_NAME'..."
  docker compose build "$API_SERVICE_NAME"
fi

# Step 2: Start (or restart) the 'api' service in detached mode
echo "[refresh_api] Starting '$API_SERVICE_NAME' in detached mode..."
docker compose up -d "$API_SERVICE_NAME"

# Step 3: Optionally follow logs
if [ "$FOLLOW_LOGS" = true ]; then
  echo "[refresh_api] Following logs for '$API_SERVICE_NAME'. Press Ctrl+C to stop."
  docker compose logs -f "$API_SERVICE_NAME"
fi