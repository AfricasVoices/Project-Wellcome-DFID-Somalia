#!/bin/bash

set -e

IMAGE_NAME=wt-fgd-cc-contacts

# Check that the correct number of arguments were provided.
if [ $# -ne 7 ]; then
    echo "Usage: sh docker-run.sh <user> <phone-uuid-path> <fgd-cc-survey-path> <coded-demog-surveys-path> <json-output-path> <fgd-csv-output-path> <cc-csv-ouput-path>"
    exit
fi

# Assign the program arguments to bash variables.
USER=$1
PHONE_UUID_TABLE=$2
FGD_CC=$3
CODED_DEMOG_SURVEYS=$4
OUTPUT_JSON=$5
OUTPUT_FGD_CSV=$6
OUTPUT_CC_CSV=$7

# Build an image for this pipeline stage.
docker build -t "$IMAGE_NAME" .

# Create a container from the image that was just built.
container="$(docker container create --env USER="$USER" "$IMAGE_NAME")"

function finish {
    # Tear down the container when done.
    docker container rm "$container" >/dev/null
}
trap finish EXIT

# Copy input data into the container
docker cp "$PHONE_UUID_TABLE" "$container:/data/phone-uuid-table.json"
docker cp "$FGD_CC" "$container:/data/input-fgd-cc.json"
docker cp "$CODED_DEMOG_SURVEYS" "$container:/data/input-demog-surveys.json"

# Run the image as a container.
docker start -a -i "$container"

# Copy the output data back out of the container
mkdir -p "$(dirname "$OUTPUT_JSON")"
docker cp "$container:/data/output.json" "$OUTPUT_JSON"

mkdir -p "$(dirname "$OUTPUT_FGD_CSV")"
docker cp "$container:/data/output-contacts-fgd.csv" "$OUTPUT_FGD_CSV"

mkdir -p "$(dirname "$OUTPUT_CC_CSV")"
docker cp "$container:/data/output-contacts-cc.csv" "$OUTPUT_CC_CSV"
