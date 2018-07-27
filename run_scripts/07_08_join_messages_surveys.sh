#!/usr/bin/env bash

set -e

if [ $# -ne 2 ]; then
    echo "Usage: sh 07_08_join_messages_surveys.sh <user> <data-root>"
    echo "Joins messages and demographic surveys on phone id, and produces CSV files for analysis"
    exit
fi

USER=$1
DATA_ROOT=$2

cd ../join_messages_surveys

mkdir -p "$DATA_ROOT/07 Joined Data"
mkdir -p "$DATA_ROOT/08 Analysis Files"

SHOWS=(
    "wt_s06e1_activation"
    )

for SHOW in "${SHOWS[@]}"
do
    echo "Merging $SHOW"

    # Note: This is still merging raw surveys (for now)
    # TODO: Export coded data.
    sh docker-run.sh "$USER" "$DATA_ROOT/02 Clean Messages/$SHOW.json" \
        "$DATA_ROOT/04 Raw Surveys/wt_demog_1.json" "$DATA_ROOT/04 Raw Surveys/wt_demog_2.json" \
        "$DATA_ROOT/04 Raw Surveys/wt_practice.json" \
        "$DATA_ROOT/07 Joined Data/$SHOW.json" "$DATA_ROOT/08 Analysis Files/$SHOW.csv"
done
