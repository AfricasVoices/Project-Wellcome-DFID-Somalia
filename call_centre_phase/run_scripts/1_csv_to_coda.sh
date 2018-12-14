set -e

if [ $# -ne 1 ]; then
    echo "Usage: sh csv_to_coda.sh <data-root>"
    exit
fi

DATA_DIR=$1

mkdir -p $DATA_DIR/1_coda_data

echo "Fetching labelled data"
cd ../call_centre_csv_to_coda
pipenv run python csv_to_coda_datasets.py "$DATA_DIR/0_dataset/cc_data.csv" "$DATA_DIR/1_coda_data"


