import argparse
import os
import time

from core_data_modules.cleaners import Codes
from core_data_modules.traced_data import Metadata, TracedData
from core_data_modules.traced_data.io import TracedDataJsonIO, TracedDataCSVIO

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Joins radio show answers with survey answers on respondents' "
                                                 "phone ids.")
    parser.add_argument("user", help="User launching this program")
    parser.add_argument("json_input_path", metavar="json-input-path",
                        help="Path to the input messages JSON file, containing a list of serialized TracedData objects")
    parser.add_argument("survey_input_path", metavar="survey-input-path",
                        help="Path to the cleaned survey JSON file, containing a list of serialized TracedData objects")
    parser.add_argument("flow_name", metavar="flow-name",
                        help="Name of activation flow from which this data was derived")
    parser.add_argument("variable_name", metavar="variable-name",
                        help="Name of message variable in flow")
    parser.add_argument("json_output_path", metavar="json-output-path",
                        help="Path to a JSON file to write processed messages to")
    parser.add_argument("csv_output_path", metavar="csv-output-path",
                        help="Path to a CSV file to write the joined dataset to")

    args = parser.parse_args()
    user = args.user
    json_input_path = args.json_input_path
    survey_input_path = args.survey_input_path
    variable_name = args.variable_name
    flow_name = args.flow_name
    json_output_path = args.json_output_path
    csv_output_path = args.csv_output_path

    message_keys = [
        "avf_phone_id",
        "{} (Run ID) - {}".format(variable_name, flow_name),
        "{} (Time) - {}".format(variable_name, flow_name),
        "{} (Text) - {}".format(variable_name, flow_name)
    ]

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

    # Load messages
    with open(json_input_path, "r") as f:
        data = TracedDataJsonIO.import_json_to_traced_data_iterable(f)

    # Load surveys
    with open(survey_input_path, "r") as f:
        surveys = TracedDataJsonIO.import_json_to_traced_data_iterable(f)

    # Add survey data to the messages
    TracedData.update_iterable(user, "avf_phone_id", data, surveys, "survey_responses")

    # Mark missing survey entries in the raw data as true missing
    for td in data:
        for key in survey_keys:
            if key not in td:
                td.append_data({key: Codes.TRUE_MISSING}, Metadata(user, Metadata.get_call_location(), time.time()))

    # Write json output
    if os.path.dirname(json_output_path) is not "" and not os.path.exists(os.path.dirname(json_output_path)):
        os.makedirs(os.path.dirname(json_output_path))
    with open(json_output_path, "w") as f:
        TracedDataJsonIO.export_traced_data_iterable_to_json(data, f, pretty_print=True)

    # Output to CSV for analysis
    export_keys = list(message_keys)
    export_keys.extend(survey_keys)

    if os.path.dirname(csv_output_path) is not "" and not os.path.exists(os.path.dirname(csv_output_path)):
        os.makedirs(os.path.dirname(csv_output_path))
    with open(csv_output_path, "w") as f:
        TracedDataCSVIO.export_traced_data_iterable_to_csv(data, f, headers=export_keys)
