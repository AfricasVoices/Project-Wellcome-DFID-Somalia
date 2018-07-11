#!/bin/bash

set -e

IMAGE_NAME=template-survey-merge-coded # TODO: Update image name to include the name of project.

# Check that the correct number of arguments were provided.
if [ $# -ne 5 ]; then
    echo "Usage: sh docker-run.sh <user> <input-file> <coding-mode> <coding-directory> <output-file>"
    exit
fi

# Assign the program arguments to bash variables.
USER=$1
INPUT_JSON=$2
CODING_MODE=$3
CODING_DIR=$4
OUTPUT_JSON=$5

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
docker cp "$CODING_DIR/." "$container:/app/data/coding"

# Run the image as a container.
docker start -a -i "$container"

# Copy the output data back out of the container
mkdir -p "$(dirname "$OUTPUT_JSON")"
docker cp "$container:/app/data/output.json" "$OUTPUT_JSON"
