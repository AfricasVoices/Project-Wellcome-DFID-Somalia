import argparse
import os
import time

from core_data_modules.traced_data import Metadata
from core_data_modules.traced_data.io import TracedDataJsonIO, TracedDataCSVIO

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Joins radio show answers with survey answers on respondents' "
                                                 "phone ids.")
    parser.add_argument("user", help="User launching this program")
    parser.add_argument("json_input_path", metavar="json-input-path",
                        help="Path to the input messages JSON file, containing a list of serialized TracedData objects")
    parser.add_argument("demog_1_input_path", metavar="demog-1-input-path",
                        help="Path to the demog_1 JSON file, containing a list of serialized TracedData objects")
    parser.add_argument("demog_2_input_path", metavar="demog-2-input-path",
                        help="Path to the demog_2 JSON file, containing a list of serialized TracedData objects")
    parser.add_argument("practice_input_path", metavar="practice-input-path",
                        help="Path to the practice JSON file, containing a list of serialized TracedData objects")
    parser.add_argument("json_output_path", metavar="json-output-path",
                        help="Path to a JSON file to write processed messages to")
    parser.add_argument("csv_output_path", metavar="csv-output-path",
                        help="Path to a CSV file to write the joined dataset to")

    args = parser.parse_args()
    user = args.user
    json_input_path = args.json_input_path
    demog_1_input_path = args.demog_1_input_path
    demog_2_input_path = args.demog_2_input_path
    practice_input_path = args.practice_input_path
    json_output_path = args.json_output_path
    csv_output_path = args.csv_output_path

    message_keys = [
        "avf_phone_id",
        "S06E01_Risk_Perception (Run ID) - wt_s06e1_activation",
        "S06E01_Risk_Perception (Time) - wt_s06e1_activation",
        "S06E01_Risk_Perception (Text) - wt_s06e1_activation"
    ]

    demog_1_keys = [
        "District (Text) - wt_demog_1",
        "Gender (Text) - wt_demog_1",
        "Urban_Rural (Text) - wt_demog_1"
    ]

    demog_2_keys = [
        "Radio_Station (Text) - wt_demog_2",
        "Age (Text) - wt_demog_2",
        "Education_Level (Text) - wt_demog_2",
        "Idp (Text) - wt_demog_2",
        "Origin_District (Text) - wt_demog_2"
    ]

    practice_keys = [
        "Cholera_Vaccination (Text) - wt_practice",
        "Household_Sickness(Text) - wt_practice",
        "Trustworthy_Advisors (Text) - wt_practice"
    ]

    def load_survey_dict(file_path):
        """
        Loads a survey from a TracedData JSON file into a dict indexed by avf_phone_id

        :param file_path: Path to survey file to load
        :type file_path: str
        :return: Dictionary mapping contact id ('avf_phone_id') to the survey TracedData for that contact.
        :rtype: dict of str -> TracedData
        """
        with open(file_path, "r") as f:
            return {td["avf_phone_id"]: td for td in TracedDataJsonIO.import_json_to_traced_data_iterable(f)}

    # Load messages
    with open(json_input_path, "r") as f:
        data = TracedDataJsonIO.import_json_to_traced_data_iterable(f)

    # Load surveys
    demog_1_table = load_survey_dict(demog_1_input_path)
    demog_2_table = load_survey_dict(demog_2_input_path)
    practice_table = load_survey_dict(practice_input_path)

    # Left join messages and demographic surveys on avf_phone_id
    # TODO: Refactor join step into CoreDataModules once satisfied with the implementation.
    # TODO: Note that this approach does not preserve the history of demographic data in the final TracedData
    for td in data:
        if td["avf_phone_id"] in demog_1_table:
            demog_1_td = demog_1_table[td["avf_phone_id"]]
            td.append_data(
                {k: demog_1_td.get(k) for k in demog_1_keys},
                Metadata(user, Metadata.get_call_location(), time.time())
            )

        if td["avf_phone_id"] in demog_2_table:
            demog_2_td = demog_2_table[td["avf_phone_id"]]
            td.append_data(
                {k: demog_2_td.get(k) for k in demog_2_keys},
                Metadata(user, Metadata.get_call_location(), time.time())
            )

        if td["avf_phone_id"] in practice_table:
            practice_td = practice_table[td["avf_phone_id"]]
            td.append_data(
                {k: practice_td.get(k) for k in practice_keys},
                Metadata(user, Metadata.get_call_location(), time.time())
            )

    # Write json output
    if os.path.dirname(json_output_path) is not "" and not os.path.exists(os.path.dirname(json_output_path)):
        os.makedirs(os.path.dirname(json_output_path))
    with open(json_output_path, "w") as f:
        TracedDataJsonIO.export_traced_data_iterable_to_json(data, f, pretty_print=True)

    # Output to CSV for analysis
    export_keys = list(message_keys)
    export_keys.extend(demog_1_keys)
    export_keys.extend(demog_2_keys)
    export_keys.extend(practice_keys)

    if os.path.dirname(csv_output_path) is not "" and not os.path.exists(os.path.dirname(csv_output_path)):
        os.makedirs(os.path.dirname(csv_output_path))
    with open(csv_output_path, "w") as f:
        TracedDataCSVIO.export_traced_data_iterable_to_csv(data, f, headers=export_keys)
