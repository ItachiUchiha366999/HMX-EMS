#!/bin/bash
# Install GSD (Get Shit Done) for Claude Code from cached package.
# This runs on every container start via postStartCommand.
# The .tgz is stored in /workspace/.gsd-cache/ which is on the host-mounted volume,
# so no internet download is needed after the first run.

set -e

CACHE_DIR="/workspace/.gsd-cache"
PACKAGE_NAME="get-shit-done-cc"

# Find the latest cached tarball
TARBALL=$(ls -t "$CACHE_DIR/${PACKAGE_NAME}-"*.tgz 2>/dev/null | head -1)

if [ -z "$TARBALL" ]; then
  echo "[GSD] No cached package found in $CACHE_DIR. Downloading..."
  npm pack "${PACKAGE_NAME}@latest" --pack-destination "$CACHE_DIR/"
  TARBALL=$(ls -t "$CACHE_DIR/${PACKAGE_NAME}-"*.tgz | head -1)
fi

echo "[GSD] Installing from $(basename "$TARBALL")..."
npm install -g "$TARBALL" --silent
get-shit-done-cc --claude --global
echo "[GSD] Ready."
