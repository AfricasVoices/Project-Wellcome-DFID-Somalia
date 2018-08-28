#!/usr/bin/env bash

set -e

if [ $# -ne 5 ]; then
    echo "Usage: sh 01b_fetch_lost_week_4_runs.sh <user> <rapid-pro-root> <rapid-pro-server> <rapid-pro-token> <data-root>"
    echo "Updates the raw messages dataset for week 4 with messages which were handled by the catchall in Rapid Pro rather than the week 4 activation flow"
    exit
fi

USER=$1
RP_DIR=$2
RP_SERVER=$3
RP_TOKEN=$4
DATA_ROOT=$5

cd ../fetch_lost_week_4_runs

SHOW="wt_s06e04_activation"

echo "Exporting show $SHOW"

sh docker-run.sh "$RP_SERVER" "$RP_TOKEN" "$USER" \
    "$DATA_ROOT/00 UUIDs/phone_uuids.json" "$DATA_ROOT/01 Raw Messages/$SHOW.json"
