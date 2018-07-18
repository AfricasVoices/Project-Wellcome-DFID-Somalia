import argparse
import os
import time

from core_data_modules.cleaners import RegexUtils
from core_data_modules.traced_data import Metadata
from core_data_modules.traced_data.io import TracedDataJsonIO, TracedDataCodingCSVIO

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Applies the given regex pattern to the specified column of "
                                                 "TracedData and outputs to a CSV which shows which items matched.")
    parser.add_argument("user", help="User launching this program", nargs=1)
    parser.add_argument("input", help="Path to the input JSON file, containing a list of serialized TracedData objects",
                        nargs=1)
    parser.add_argument("key_of_raw", metavar="key-of-raw",
                        help="Key in TracedData of item to apply regex pattern to", nargs=1)
    parser.add_argument("regex_pattern", metavar="regex-pattern",
                        help="Python regex pattern to apply to each TracedData item", nargs=1)
    parser.add_argument("json_output", metavar="json-output",
                        help="Path to a JSON file to write processed messages to", nargs=1)
    parser.add_argument("matches_csv_output", metavar="matches-csv-out",
                        help="Path to a CSV file to write regex match results to", nargs=1)

    args = parser.parse_args()
    user = args.user[0]
    input_path = args.input[0]
    key_of_raw = args.key_of_raw[0]
    pattern = args.regex_pattern[0]
    json_output_path = args.json_output[0]
    matches_csv_output_path = args.matches_csv_output[0]

    key_of_matches = "{}_matches".format(key_of_raw)

    # Load data from JSON file
    with open(input_path, "r") as f:
        data = TracedDataJsonIO.import_json_to_traced_data_iterable(f)

    # Apply the regex pattern to the data
    for td in data:
        td.append_data(
            {
                key_of_matches: RegexUtils.has_matches(td[key_of_raw], pattern)
            },
            Metadata(user, Metadata.get_call_location(), time.time())
        )

    # Write json output
    if os.path.dirname(json_output_path) is not "" and not os.path.exists(os.path.dirname(json_output_path)):
        os.makedirs(os.path.dirname(json_output_path))
    with open(json_output_path, "w") as f:
        TracedDataJsonIO.export_traced_data_iterable_to_json(data, f, pretty_print=True)

    # Output to a CSV listing de-duplicated responses and whether or not they matched the regex pattern
    if os.path.dirname(matches_csv_output_path) is not "" and not os.path.exists(os.path.dirname(matches_csv_output_path)):
        os.makedirs(os.path.dirname(matches_csv_output_path))
    with open(matches_csv_output_path, "w") as f:
        TracedDataCodingCSVIO.export_traced_data_iterable_to_coding_csv_with_scheme(
            data, key_of_raw, key_of_matches, f)
