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

mkdir -p "$DATA_ROOT/07 Joined Raw Data"
mkdir -p "$DATA_ROOT/08 Joined Raw Data CSVs"

SHOWS=(
    "wt_s06e1_activation" S06E01_Risk_Perception
    "wt_s06e2_activation" S06E02_Cholera_Preparedness
    "wt_s06e03_activation" S06E03_Outbreak_Knowledge
    "wt_s06e04_activation" S06E04_Cholera_Recurrency
    "wt_s06e05_activation" S06E05_Water_Quality
    )

for i in $(seq 0 $((${#SHOWS[@]} / 2 - 1)))
do
    SHOW="${SHOWS[2 * i]}"
    VARIABLE="${SHOWS[2 * i + 1]}"

    echo "Joining raw data for $SHOW"

    # Note: This is still merging raw surveys (for now)
    sh docker-run.sh "$USER" "$DATA_ROOT/02 Clean Messages/$SHOW.json" \
        "$DATA_ROOT/05 Auto-Coded/surveys.json" "$SHOW" "$VARIABLE" \
        "$DATA_ROOT/07 Joined Raw Data/$SHOW.json" "$DATA_ROOT/08 Joined Raw Data CSVs/$SHOW.csv"
done
