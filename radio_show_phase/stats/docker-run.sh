#!/bin/bash

set -e

IMAGE_NAME=wt-stats

# Check that the correct number of arguments were provided.
if [ $# -ne 4 ]; then
    echo "Usage: sh docker-run.sh <user> <messages-input-path> <survey-input-path> <stats-output-path>"
    exit
fi

# Assign the program arguments to bash variables.
USER=$1
INPUT_MESSAGES_DIR=$2
INPUT_SURVEY=$3
OUTPUT_STATS=$4

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
docker cp "$INPUT_SURVEY" "$container:/data/survey-input.json"
docker cp "$INPUT_MESSAGES_DIR/." "$container:/data/messages-input"

# Run the container
docker start -a -i "$container"

# Copy the output data back out of the container
mkdir -p "$(dirname "$OUTPUT_STATS")"
docker cp "$container:/data/stats-output.csv" "$OUTPUT_STATS"
