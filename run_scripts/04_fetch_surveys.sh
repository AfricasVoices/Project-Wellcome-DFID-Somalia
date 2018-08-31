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

mkdir -p "$DATA_ROOT/04 Raw Surveys"

SURVEYS=(
    "wt_demog_1"
    "wt_demog_2"
    "wt_practice"
    "wt_fgd_cc"
    )

for SURVEY in ${SURVEYS[@]}
do
    echo "Exporting survey $SURVEY"

    sh docker-run.sh "$RP_SERVER" "$RP_TOKEN" "$SURVEY" "$USER" latest-only \
        "$DATA_ROOT/00 UUIDs/phone_uuids.json" "$DATA_ROOT/04 Raw Surveys/$SURVEY.json"
done
