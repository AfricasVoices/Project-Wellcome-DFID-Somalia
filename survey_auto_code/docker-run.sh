#!/bin/bash

set -e

IMAGE_NAME=wt-survey-auto-code

# Check that the correct number of arguments were provided.
if [ $# -ne 6 ]; then
    echo "Usage: sh docker-run.sh <user> <demog-1-input-path> <demog-2-input-path> <practice-input-path> <json-output-path> <coded-output-path>"
    exit
fi

# Assign the program arguments to bash variables.
USER=$1
INPUT_DEMOG_1=$2
INPUT_DEMOG_2=$3
INPUT_PRACTICE=$4
OUTPUT_JSON=$5
CODING_DIR=$6

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
docker cp "$INPUT_DEMOG_1" "$container:/data/input-demog-1.json"
docker cp "$INPUT_DEMOG_2" "$container:/data/input-demog-2.json"
docker cp "$INPUT_PRACTICE" "$container:/data/input-practice.json"

# Run the image as a container.
docker start -a -i "$container"

# Copy the output data back out of the container
mkdir -p "$(dirname "$OUTPUT_JSON")"
docker cp "$container:/data/output.json" "$OUTPUT_JSON"

mkdir -p "$CODING_DIR"
docker cp "$container:/data/coding/." "$CODING_DIR"
