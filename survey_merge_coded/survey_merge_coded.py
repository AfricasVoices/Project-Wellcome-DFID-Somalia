import argparse
import os
from os import path

from core_data_modules.traced_data.io import TracedDataJsonIO, TracedDataCodaIO, TracedDataCodingCSVIO
from core_data_modules.util import IOUtils

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merges manually cleaned files back into a traced data file.")
    parser.add_argument("user", help="User launching this program, for use by TracedData Metadata")
    parser.add_argument("json_input_path", metavar="json-input-path",
                        help="Path to JSON input file, which contains a list of TracedData objects")
    parser.add_argument("coded_input_path", metavar="coded-input-path",
                        help="Directory to read coding files from")
    parser.add_argument("json_output_path", metavar="json-output-path",
                        help="Path to a JSON file to write merged results to")

    args = parser.parse_args()
    user = args.user
    json_input_path = args.json_input_path
    coded_input_path = args.coded_input_path
    json_output_path = args.json_output_path

    survey_keys = [
        "District (Text) - wt_demog_1",
        "Gender (Text) - wt_demog_1",
        "Urban_Rural (Text) - wt_demog_1",

        "Radio_Station (Text) - wt_demog_2",
        "Age (Text) - wt_demog_2",
        "Education_Level (Text) - wt_demog_2",
        "Idp (Text) - wt_demog_2",
        "Origin_District (Text) - wt_demog_2",

        "Cholera_Vaccination (Text) - wt_practice",
        "Household_Sickness (Text) - wt_practice",
        "Trustworthy_Advisors (Text) - wt_practice"
    ]

    # Load data from JSON file
    with open(json_input_path, "r") as f:
        surveys = TracedDataJsonIO.import_json_to_traced_data_iterable(f)

    # Merge manually coded Coda files into the cleaned dataset
    for key in survey_keys:
        coda_file_path = path.join(coded_input_path, "{}_coded.csv".format(key.split(" ")[0]))

        if not path.exists(coda_file_path):
            print("Warning: No Coda file found for key '{}'".format(key))
            continue

        with open(coda_file_path, "r") as f:
            TracedDataCodaIO.import_coda_to_traced_data_iterable(
                user, surveys, key, {key.split(" ")[0]: "{}_coded".format(key)}, f, True)

    # Write coded data back out to disk
    IOUtils.ensure_dirs_exist_for_file(json_output_path)
    with open(json_output_path, "w") as f:
        TracedDataJsonIO.export_traced_data_iterable_to_json(surveys, f, pretty_print=True)
