#!/usr/bin/env bash

set -e

if [ $# -ne 2 ]; then
    echo "Usage: sh 05_06_survey_auto_code.sh"
    echo "Exports columns of demog 1 to Coda."  # TODO: Update description once Somali regexes are enabled.
    exit
fi

USER=$1
DATA_ROOT=$2

cd ../survey_auto_code

mkdir -p "$DATA_ROOT/05 Auto-Coded"
mkdir -p "$DATA_ROOT/06 Coda Files"

# Auto-code wt_demog_1 and export to Coda.
# TODO: Auto-code the other surveys and export to Coda.
sh docker-run.sh "$USER" "$DATA_ROOT/04 Raw Surveys/wt_demog_1.json" \
    "$DATA_ROOT/05 Auto-Coded/wt_demog_1.json" "$DATA_ROOT/06 Coda Files/"

