#!/bin/bash

set -e

IMAGE_NAME=wt-messages

# Check that the correct number of arguments were provided.
if [ $# -ne 5 ]; then
    echo "Usage: sh docker-run.sh <user> <json-input-path> <json-output-path> <csv-output-path> <coda-output-path>"
    exit
fi

# Assign the program arguments to bash variables.
USER=$1
INPUT_JSON=$2
OUTPUT_JSON=$3
OUTPUT_CSV=$4
OUTPUT_CODA=$5

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
docker cp "$INPUT_JSON" "$container:/data/input.json"

# Run the container
docker start -a -i "$container"

# Copy the output data back out of the container
mkdir -p "$(dirname "$OUTPUT_JSON")"
docker cp "$container:/data/output.json" "$OUTPUT_JSON"

mkdir -p "$(dirname "$OUTPUT_CSV")"
docker cp "$container:/data/output.csv" "$OUTPUT_CSV"

mkdir -p "$(dirname "$OUTPUT_CODA")"
docker cp "$container:/data/output-coda.csv" "$OUTPUT_CODA"
