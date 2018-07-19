#!/bin/bash

set -e

IMAGE_NAME=wt-regex-tester

# Check that the correct number of arguments were provided.
if [ $# -ne 6 ]; then
    echo "Usage: sh docker-run.sh <user> <input-json> <key-of-raw> <regex-pattern> <output-json> <output-matches-csv>"
    exit
fi

# Assign the program arguments to bash variables.
USER=$1
INPUT_JSON=$2
KEY_OF_RAW=$3
REGEX_PATTERN=$4
OUTPUT_JSON=$5
OUTPUT_MATCHES_CSV=$6

# Build an image for this pipeline stage.
docker build -t "$IMAGE_NAME" .

# Create a container from the image that was just built.
container="$(docker container create --env USER="$USER" --env KEY_OF_RAW="$KEY_OF_RAW" --env REGEX_PATTERN="$REGEX_PATTERN" "$IMAGE_NAME")"

function finish {
    # Tear down the container when done.
    docker container rm "$container" >/dev/null
}
trap finish EXIT

# Copy input data into the container
docker cp "$INPUT_JSON" "$container:/data/input.json"

# Run the container
docker start -a -i "$container"

# Copy the output data back out of the container
mkdir -p "$(dirname "$OUTPUT_JSON")"
docker cp "$container:/data/output.json" "$OUTPUT_JSON"

mkdir -p "$(dirname "$OUTPUT_MATCHES_CSV")"
docker cp "$container:/data/output.csv" "$OUTPUT_MATCHES_CSV"
