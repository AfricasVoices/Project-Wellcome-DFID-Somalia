#!/usr/bin/env bash

set -e

if [ $# -ne 1 ]; then
    echo "Usage: sh checkout_rapid_pro_tools.sh <rapid-pro-dir>"
    echo "Ensures that a copy of the RapidProTools project exists in  'rapid-pro-root' by cloning/fetching as, "
    echo "necessary, and checking-out the version needed by this project"
    exit
fi

RAPID_PRO_DIR="$1"

RAPID_PRO_REPO="https://github.com/AfricasVoices/RapidProTools.git"
TAG="v0.1.0"

mkdir -p "$RAPID_PRO_DIR"
cd "$RAPID_PRO_DIR"

# If the RAPID_PRO_DIR does not contain a git repository, clone the rapid pro repo
if ! [ -d .git ]; then
    git clone "$RAPID_PRO_REPO" .
fi

# Check that this repository is connected to the correct remote.
# (this ensures we are in the correct repository and can fetch new changes later if we need to)
if [ $(git config --get remote.origin.url) != "$RAPID_PRO_REPO" ]; then
    echo "Error: Git repository in RAPID_PRO_ROOT does not have its origin set to $RAPID_PRO_REPO"
    exit 1
fi

# If the provided tag wasn't found, run git fetch in case the remote has been updated
if ! [ $(git tag -l "$TAG") ]; then
    git fetch --tags
fi

# Checkout the requested tag
git checkout -q "$TAG"
