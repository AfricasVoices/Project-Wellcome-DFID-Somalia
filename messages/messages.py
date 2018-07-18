import argparse
import os

from core_data_modules.traced_data.io import TracedDataJsonIO, TracedDataCSVIO

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cleans a list of messages, and outputs to formats "
                                                 "suitable for subsequent analysis")
    parser.add_argument("user", help="User launching this program", nargs=1)
    parser.add_argument("input", help="Path to the input JSON file, containing a list of serialized TracedData objects",
                        nargs=1)
    parser.add_argument("json_output", metavar="json-output",
                        help="Path to a JSON file to write processed messages to", nargs=1)
    parser.add_argument("csv_output", metavar="csv-output",
                        help="Path to a CSV file to write processed messages to", nargs=1)

    args = parser.parse_args()
    user = args.user[0]
    input_path = args.input[0]
    json_output_path = args.json_output[0]
    csv_output_path = args.csv_output[0]

    # Load data from JSON file
    with open(input_path, "r") as f:
        data = TracedDataJsonIO.import_json_to_traced_data_iterable(f)

    # TODO: Clean/filter messages

    # Write json output
    if os.path.dirname(json_output_path) is not "" and not os.path.exists(os.path.dirname(json_output_path)):
        os.makedirs(os.path.dirname(json_output_path))
    with open(json_output_path, "w") as f:
        TracedDataJsonIO.export_traced_data_iterable_to_json(data, f, pretty_print=True)

    # Output to a more human-friendly CSV.
    if os.path.dirname(csv_output_path) is not "" and not os.path.exists(os.path.dirname(csv_output_path)):
        os.makedirs(os.path.dirname(csv_output_path))
    with open(csv_output_path, "w") as f:
        TracedDataCSVIO.export_traced_data_iterable_to_csv(
            data, f, headers=[
                "avf_phone_id",
                "S06E01_Risk_Perception (Run ID) - wt_s06e1_activation",
                "S06E01_Risk_Perception (Time) - wt_s06e1_activation",
                "S06E01_Risk_Perception (Text) - wt_s06e1_activation"
            ]
        )
