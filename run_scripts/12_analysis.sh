#!/usr/bin/env bash

set -e

if [ $# -ne 2 ]; then
    echo "Usage: sh 11_stats.sh <user> <data-root>"
    echo "Produces summary stats for surveys and shows"
    exit
fi

USER=$1
DATA_ROOT=$2

cd ../analysis_file

mkdir -p "$DATA_ROOT/12 Analysis"

sh docker-run.sh "$USER" "$DATA_ROOT/02 Clean Messages/" "$DATA_ROOT/10 Manually Coded/surveys.json" \
    "$DATA_ROOT/12 Analysis/stats.csv"
