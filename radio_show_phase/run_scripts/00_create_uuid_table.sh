#!/usr/bin/env bash

set -e

if [ $# -ne 1 ]; then
    echo "Usage: sh 00_create_uuid_table.sh <data-root>"
    echo "Writes an empty UUID table for phone numbers."
    exit
fi

DATA_DIR=$1

mkdir -p "$DATA_DIR/00 UUIDs"

echo "{}" >"$DATA_DIR/00 UUIDs/phone_uuids.json"
