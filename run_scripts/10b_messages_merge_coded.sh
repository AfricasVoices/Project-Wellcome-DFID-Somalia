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

SHOWS=(
    1 "wt_s06e1_activation"
    2 "wt_s06e2_activation"
    3 "wt_s06e03_activation"
    )

for i in $(seq 0 $((${#SHOWS[@]} / 2 - 1)))
do
    SHOW_NUMBER="${SHOWS[2 * i]}"
    SHOW_NAME="${SHOWS[2 * i + 1]}"

    echo "Merging $SHOW_NAME"

    sh docker-run.sh "$USER" "$DATA_ROOT/02 Clean Messages/$SHOW_NAME.json" \
        "$DATA_ROOT/09 Coded Coda Files/${SHOW_NAME}_coded.csv" "$SHOW_NUMBER" \
        "$DATA_ROOT/10 Manually Coded/$SHOW_NAME.json"
done
