#!/usr/bin/env bash

set -e

if [ $# -ne 5 ]; then
    echo "Usage: sh 01_fetch_messages.sh <user> <rapid-pro-root> <rapid-pro-server> <rapid-pro-token> <data-root>"
    echo "Downloads radio show answers from each show"
    exit
fi

USER=$1
RP_DIR=$2
RP_SERVER=$3
RP_TOKEN=$4
DATA_ROOT=$5

cd "$RP_DIR"

mkdir -p "$DATA_ROOT/01 Raw Messages"

SHOWS=(
    "wt_s06e1_activation"
    "wt_s06e2_activation"
    "wt_s06e03_activation"
    "wt_s06e04_activation"
    )

for SHOW in ${SHOWS[@]}
do
    echo "Exporting show $SHOW"

    sh docker-run.sh "$RP_SERVER" "$RP_TOKEN" "$SHOW" "$USER" all \
        "$DATA_ROOT/00 UUIDs/phone_uuids.json" "$DATA_ROOT/01 Raw Messages/$SHOW.json"
done
