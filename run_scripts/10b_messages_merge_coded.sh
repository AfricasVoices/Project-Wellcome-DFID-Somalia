#!/usr/bin/env bash

set -e

if [ $# -ne 2 ]; then
    echo "Usage: sh 10b_messages_merge_coded.sh <user> <data-root>"
    echo "Applies codes from a Coda file to show responses"
    exit
fi

USER=$1
DATA_ROOT=$2

cd ../messages_merge_coded

mkdir -p "$DATA_ROOT/10 Manually Coded"

SHOW="wt_s06e1_activation"

sh docker-run.sh "$USER" "$DATA_ROOT/02 Clean Messages/$SHOW.json" \
    "$DATA_ROOT/09 Coded Coda Files/${SHOW}_coded.csv" "$DATA_ROOT/10 Manually Coded/$SHOW.json"
