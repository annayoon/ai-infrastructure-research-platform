#!/bin/zsh
# Syncs the data directories that are gitignored (downloads/, corpus_text/,
# vector_db/) from this machine to the company server, since `git push`
# alone will not carry them over.
#
# Edit SERVER_HOST and SERVER_PATH below, then run after each local
# daily_update.sh run (or before deploying data changes).

SERVER_HOST="<user>@<server-ip>"
SERVER_PATH="/opt/ai-infrastructure-research-platform"

set -e
cd "$(dirname "$0")/.."

for dir in downloads corpus_text vector_db; do
  echo "=== Syncing $dir ==="
  rsync -avz --delete "$dir/" "$SERVER_HOST:$SERVER_PATH/$dir/"
done

echo "=== Done ==="
