import argparse
import os

from core_data_modules.traced_data.io import TracedDataJsonIO, TracedDataCSVIO, TracedDataCodaIO
from core_data_modules.util import IOUtils

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cleans a list of messages, and outputs to formats "
                                                 "suitable for subsequent analysis")
    parser.add_argument("user", help="User launching this program")
    parser.add_argument("json_input_path", metavar="json-input-path",
                        help="Path to the input JSON file, containing a list of serialized TracedData objects")
    parser.add_argument("flow_name", metavar="flow-name",
                        help="Name of activation flow from which this data was derived")
    parser.add_argument("variable_name", metavar="variable-name",
                        help="Name of message variable in flow")
    parser.add_argument("json_output_path", metavar="json-output-path",
                        help="Path to a JSON file to write processed messages to")
    parser.add_argument("csv_output_path", metavar="csv-output-path",
                        help="Path to a CSV file to write processed messages to")
    parser.add_argument("coda_output_path", metavar="coda-output-path",
                        help="Path to a Coda file to write processed messages to")

    args = parser.parse_args()
    user = args.user
    json_input_path = args.json_input_path
    variable_name = args.variable_name
    flow_name = args.flow_name
    json_output_path = args.json_output_path
    csv_output_path = args.csv_output_path
    coda_output_path = args.coda_output_path

    # Load data from JSON file
    with open(json_input_path, "r") as f:
        data = TracedDataJsonIO.import_json_to_traced_data_iterable(f)

    # Filter for runs which contain a response to this week's question.
    data = list(filter(lambda td: "{} (Text) - {}".format(variable_name, flow_name) in td, data))

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
                "{} (Run ID) - {}".format(variable_name, flow_name),
                "{} (Time) - {}".format(variable_name, flow_name),
                "{} (Text) - {}".format(variable_name, flow_name)
            ]
        )

    # Output messages to Coda
    IOUtils.ensure_dirs_exist_for_file(coda_output_path)
    with open(coda_output_path, "w") as f:
        TracedDataCodaIO.export_traced_data_iterable_to_coda(
            data, "{} (Text) - {}".format(variable_name, flow_name), f)
