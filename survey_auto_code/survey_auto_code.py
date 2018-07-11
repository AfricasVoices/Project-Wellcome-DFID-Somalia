import argparse
import os
from os import path

from core_data_modules.traced_data.io import TracedDataJsonIO, TracedDataCodaIO, TracedDataCodingCSVIO

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cleans a survey and exports to Coda or a Coding for manual "
                                                 "verification and coding")
    parser.add_argument("user", help="User launching this program", nargs=1)
    parser.add_argument("input", help="Path to input file, containing a list of TracedData objects as JSON", nargs=1)
    parser.add_argument("json_output", metavar="json-output",
                        help="Path to the input JSON file, containing a list of serialized TracedData objects", nargs=1)
    parser.add_argument("coding_output_mode", metavar="coding-output-mode",
                        help="File format to export data to for coding."
                             "Accepted values are 'coda' or 'coding-csv'", nargs=1, choices=["coda", "coding-csv"])
    parser.add_argument("coding_output_directory", metavar="coding-output-directory",
                        help="Directory to write coding files to", nargs=1)

    args = parser.parse_args()
    user = args.user[0]
    input_path = args.input[0]
    json_output_path = args.json_output[0]
    coding_mode = args.coding_output_mode[0]
    coded_output_directory = args.coding_output_directory[0]

    # Load data from JSON file
    with open(input_path, "r") as f:
        data = TracedDataJsonIO.import_json_to_traced_data_iterable(f)

    # TODO: Clean survey data

    # Write json output
    if os.path.dirname(json_output_path) is not "" and not os.path.exists(os.path.dirname(json_output_path)):
        os.makedirs(os.path.dirname(json_output_path))
    with open(json_output_path, "w") as f:
        TracedDataJsonIO.export_traced_data_iterable_to_json(data, f, pretty_print=True)

    # Output for manual verification + coding
    if coding_mode == "coda":
        # Write Coda output
        if not os.path.exists(coded_output_directory):
            os.makedirs(coded_output_directory)

        # TODO: Set the <example-arguments> to export a particular column e.g. "age", "age_clean", "Age"
        with open(path.join(coded_output_directory, "<output-file>.csv"), "w") as f:
            TracedDataCodaIO.export_traced_data_iterable_to_coda_with_scheme(
                data, "<key-of-raw>", "<key-of-coded>", "<name-in-Coda>", f)

        # TODO: Re-use the above code sample to export other columns which need verifying/coding.
    else:
        assert coding_mode == "coding-csv", "coding_mode was not one of 'coda' or 'coding-csv'"

        # Write Coding CSV output
        if not os.path.exists(coded_output_directory):
            os.makedirs(coded_output_directory)

        # TODO: Set the <example-arguments> to export a particular column e.g. "age", "age_clean", "Age"
        with open(path.join(coded_output_directory, "<output-file>.csv"), "w") as f:
            TracedDataCodingCSVIO.export_traced_data_iterable_to_coding_csv_with_scheme(
                data, "<key-of-raw>", "<key-of-coded>", f)

        # TODO: Re-use the above code sample to export other columns which need verifying/coding.
