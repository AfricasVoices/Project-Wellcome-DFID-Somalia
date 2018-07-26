import argparse
import os
import time
from os import path

from core_data_modules.cleaners import somali
from core_data_modules.traced_data import Metadata
from core_data_modules.traced_data.io import TracedDataJsonIO, TracedDataCodaIO

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cleans the wt_demog_1 survey and exports variables to Coda for "
                                                 "manual verification and coding")
    parser.add_argument("user", help="User launching this program, for use by TracedData Metadata")
    parser.add_argument("demog_1_input_path", metavar="demog-1-input-path",
                        help="Path to input file, containing a list of serialized TracedData objects as JSON")
    parser.add_argument("json_output_path", metavar="json-output-path",
                        help="Path to a JSON file to write processed TracedData messages to")
    parser.add_argument("coded_output_path", metavar="coding-output-path",
                        help="Directory to write coding files to")

    args = parser.parse_args()
    user = args.user
    demog_1_input_path = args.demog_1_input_path
    json_output_path = args.json_output_path
    coded_output_path = args.coded_output_path

    cleaning_config = {
        "District (Text) - wt_demog_1": somali.DemographicCleaner.clean_somalia_district,
        "Gender (Text) - wt_demog_1": somali.DemographicCleaner.clean_gender,
        "Urban_Rural (Text) - wt_demog_1": somali.DemographicCleaner.clean_urban_rural
    }

    # Load data from JSON file
    with open(demog_1_input_path, "r") as f:
        data = TracedDataJsonIO.import_json_to_traced_data_iterable(f)

    # TODO: Extend to add another argument for demog2, load this survey, and merge with demog1.
    # TODO: Then we don't have to maintain parallel pipelines for data which was arbitrarily separated to begin with.

    # Clean the survey
    for td in data:
        for key, cleaner in cleaning_config.items():
            if key in td:
                td.append_data(
                    {"{}_clean".format(key): cleaner(td[key])},
                    Metadata(user, Metadata.get_call_location(), time.time())
                )

    # Set missing entries in the raw data to 'NA'
    for td in data:
        for key in cleaning_config:
            if key not in td:
                td.append_data({key: "NA"}, Metadata(user, Metadata.get_call_location(), time.time()))

    # Write json output
    if os.path.dirname(json_output_path) is not "" and not os.path.exists(os.path.dirname(json_output_path)):
        os.makedirs(os.path.dirname(json_output_path))
    with open(json_output_path, "w") as f:
        TracedDataJsonIO.export_traced_data_iterable_to_json(data, f, pretty_print=True)

    # Output for manual verification + coding
    if not os.path.exists(coded_output_path):
        os.makedirs(coded_output_path)

    for key in cleaning_config.keys():
        output_file_path = path.join(coded_output_path, "{}.csv".format(key.split(" ")[0]))
        with open(output_file_path, "w") as f:
            TracedDataCodaIO.export_traced_data_iterable_to_coda_with_scheme(
                data, key, "{}_clean".format(key), key.split(" ")[0], f)
