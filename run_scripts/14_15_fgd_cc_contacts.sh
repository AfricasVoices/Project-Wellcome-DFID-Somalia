#!/usr/bin/env bash

set -e

if [ $# -ne 2 ]; then
    echo "Usage: sh 14_15_fgd_cc_contacts <user> <data-root>"
    echo "Produces a CSV containing contacts for follow-up in focus group discussions/call centre interviews"
    exit
fi

USER=$1
DATA_ROOT=$2

mkdir -p "$DATA_ROOT/14 FGD_CC Contacts"
mkdir -p "$DATA_ROOT/15 FGD_CC Contacts CSVs"

cd ../fgd_cc_contacts

echo "Generating FGD/CC Contacts CSV"

sh docker-run.sh "$USER" "$DATA_ROOT/00 UUIDs/phone_uuids.json" \
   "$DATA_ROOT/04 Raw Surveys/wt_fgd_cc.json" "$DATA_ROOT/10 Manually Coded/surveys.json" \
   "$DATA_ROOT/14 FGD_CC Contacts/fgd_cc_contacts.json" \
   "$DATA_ROOT/15 FGD_CC Contacts CSVs/fgd_contacts.csv" "$DATA_ROOT/15 FGD_CC Contacts CSVs/cc_contacts.csv"
