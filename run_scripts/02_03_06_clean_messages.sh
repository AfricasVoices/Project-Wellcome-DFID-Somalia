#!/usr/bin/env bash

set -e

if [ $# -ne 2 ]; then
    echo "Usage: sh 02_03_06_clean_messages.sh <user> <data-root>"
    echo "Cleans radio show answers, and exports to CSVs for analysis."
    exit
fi

USER=$1
DATA_ROOT=$2

cd ../messages

mkdir -p "$DATA_ROOT/02 Clean Messages"
mkdir -p "$DATA_ROOT/03 Message CSVs"
mkdir -p "$DATA_ROOT/06 Coda Files"

SHOWS=(
    "wt_s06e1_activation"
    )

for SHOW in "${SHOWS[@]}"
do
    echo "Cleaning $SHOW"

    sh docker-run.sh "$USER" "$DATA_ROOT/01 Raw Messages/$SHOW.json" \
        "$DATA_ROOT/02 Clean Messages/$SHOW.json" "$DATA_ROOT/03 Message CSVs/$SHOW.csv" \
        "$DATA_ROOT/06 Coda files/$SHOW.csv"
done
