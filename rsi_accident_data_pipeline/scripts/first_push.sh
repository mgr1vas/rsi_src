#!/usr/bin/env bash
set -euo pipefail
if [ "$#" -ne 1 ]; then
  echo "Usage: ./scripts/first_push.sh https://github.com/ORG/REPO.git"
  exit 1
fi

git init
git add .
git commit -m "Initial Crete accident data pipeline"
git branch -M main
git remote add origin "$1"
git push -u origin main
