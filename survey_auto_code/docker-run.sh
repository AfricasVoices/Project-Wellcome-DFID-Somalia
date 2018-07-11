#!/bin/bash

set -e

IMAGE_NAME=template-survey-auto-code # TODO: Update image name to include the name of project.

# Check that the correct number of arguments were provided.
if [ $# -ne 5 ]; then
    echo "Usage: sh docker-run.sh <user> <input-file> <output-file> <coding-mode> <coding-directory>"
    exit
fi

# Assign the program arguments to bash variables.
USER=$1
INPUT_JSON=$2
OUTPUT_JSON=$3
CODING_MODE=$4
CODING_DIR=$5

# Build an image for this pipeline stage.
docker build -t "$IMAGE_NAME" .

# Create a container from the image that was just built.
container="$(docker container create --env USER="$USER" --env CODING_MODE="$CODING_MODE" "$IMAGE_NAME")"

function finish {
    # Tear down the container when done.
    docker container rm "$container" >/dev/null
}
trap finish EXIT

# Copy input data into the container
docker cp "$INPUT_JSON" "$container:/app/data/input.json"

# Run the image as a container.
docker start -a -i "$container"

# Copy the output data back out of the container
mkdir -p "$(dirname "$OUTPUT_JSON")"
docker cp "$container:/app/data/output.json" "$OUTPUT_JSON"

mkdir -p "$CODING_DIR"
docker cp "$container:/app/data/coding/." "$CODING_DIR"
