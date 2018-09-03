#!/usr/bin/env bash

set -e

if [ $# -ne 2 ]; then
    echo "Usage: sh 05_06_survey_auto_code.sh <user> <data-root>"
    echo "Merges and cleans the raw demographic and practice surveys, and exports to Coda files for manual verification/coding"
    exit
fi

USER=$1
DATA_ROOT=$2

cd ../survey_auto_code

mkdir -p "$DATA_ROOT/05 Auto-Coded"
mkdir -p "$DATA_ROOT/06 Coda Files"

echo "Auto-coding surveys"

sh docker-run.sh "$USER" "$DATA_ROOT/04 Raw Surveys/wt_demog_1.json" "$DATA_ROOT/04 Raw Surveys/wt_demog_2.json" \
    "$DATA_ROOT/04 Raw Surveys/wt_practice.json" "$DATA_ROOT/09 Coded Coda Files/" \
    "$DATA_ROOT/05 Auto-Coded/surveys.json" "$DATA_ROOT/06 Coda Files/"
