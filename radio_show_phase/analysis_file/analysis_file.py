import argparse
import time
from os import path

from core_data_modules.cleaners import Codes
from core_data_modules.traced_data import TracedData, Metadata
from core_data_modules.traced_data.io import TracedDataJsonIO, TracedDataCSVIO
from core_data_modules.util import IOUtils

from lib.aggregate_traced_data import AggregateTracedData
from lib.analysis_keys import AnalysisKeys
from lib.code_books import CodeBooks

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generates a file for analysis from the cleaned and coded shows "
                                                 "and survey responses")
    parser.add_argument("user", help="User launching this program")
    parser.add_argument("messages_input_dir", metavar="messages-input-dir",
                        help="Path to a directory containing JSON files of responses to each of the shows in this "
                             "project. Each JSON file should contain a list of serialized TracedData objects")
    parser.add_argument("survey_input_path", metavar="survey-input-path",
                        help="Path to a coded survey JSON file, containing a list of serialized TracedData objects")
    parser.add_argument("json_output_path", metavar="json-output-path",
                        help="Path to a JSON file to write serialized TracedData items to after modification by this"
                             "pipeline stage")
    parser.add_argument("csv_output_path", metavar="csv-output-path",
                        help="Path to a CSV file to write the summarised stats to")

    args = parser.parse_args()
    user = args.user
    messages_input_dir = args.messages_input_dir
    survey_input_path = args.survey_input_path
    json_output_path = args.json_output_path
    csv_output_path = args.csv_output_path


    def load_show(show_name):
        show_path = path.join(messages_input_dir, "{}.json".format(show_name))
        if not path.exists(show_path):
            print("Warning: No show found with file name '{}.json'".format(show_name))
            return []
        with open(show_path, "r") as f:
            return list(TracedDataJsonIO.import_json_to_traced_data_iterable(f))


    # Load surveys
    with open(survey_input_path, "r") as f:
        surveys = TracedDataJsonIO.import_json_to_traced_data_iterable(f)

    shows = {
        1: "wt_s06e1_activation",
        2: "wt_s06e2_activation",
        3: "wt_s06e03_activation",
        4: "wt_s06e04_activation",
        5: "wt_s06e05_activation"
    }

    # Produce output columns for each input message
    all_messages = []
    all_show_keys = {
        1: set(),
        2: set(),
        3: set(),
        4: set(),
        5: set()
    }
    trustworthy_advisors_keys = set()
    outbreak_keys = set()
    trustworthy_advisors_raw_key = "Trustworthy_Advisors (Text) - wt_practice"
    for show_number, show_name in shows.items():
        show_messages = load_show(show_name)
        TracedData.update_iterable(user, "avf_phone_id", show_messages, surveys, "surveys")

        for td in show_messages:
            AnalysisKeys.set_analysis_keys(user, show_number, td)
            AnalysisKeys.set_matrix_analysis_keys(user, all_show_keys[show_number], show_number, td)

            AnalysisKeys.set_matrix_keys(
                user, td, trustworthy_advisors_keys, "{}_coded".format(trustworthy_advisors_raw_key),
                "trustworthy_advisors_clean")

            AnalysisKeys.set_matrix_keys(
                user, td, outbreak_keys, "{}_outbreak_coded".format(trustworthy_advisors_raw_key),
                "outbreak_action")

        all_messages.extend(show_messages)

    # Set keys to other shows to NS
    for td in all_messages:
        other_show_answers = dict()
        for show_number, show_keys in all_show_keys.items():
            if td["radio_show"] != show_number:
                other_show_answers["radio_q{}".format(show_number)] = Codes.TRUE_MISSING  # TODO: Asserts
                for output_key in show_keys:
                    other_show_answers[output_key] = Codes.TRUE_MISSING
        td.append_data(other_show_answers, Metadata(user, Metadata.get_call_location(), time.time()))

    # Group input messages by participant/day
    print("Aggregating")
    collated_messages = AggregateTracedData.aggregate_by_respondent_and_date(user, all_messages)

    print("  Pre-aggregation: {}".format(len(all_messages)))
    print("  Post-aggregation: {}".format(len(collated_messages)))

    all_messages = collated_messages  # TODO: Undo this hack
    print(len(all_messages))

    # Apply code-books
    code_books = {
        "district_clean": CodeBooks.district,
        "urban_rural_clean": CodeBooks.urban_rural,
        "gender_clean": CodeBooks.gender,

        "radio_station_clean": CodeBooks.radio_station,
        # Skip age_clean because not applying code book
        "education_clean": CodeBooks.education,
        "idp_clean": CodeBooks.yes_no,
        "origin_district_clean": CodeBooks.district,

        "household_sickness_clean": CodeBooks.yes_no,
        "sickness_adult_child": CodeBooks.sickness_adult_child,
        "cholera_vaccination_clean": CodeBooks.cholera_vaccination,

        "message_type": CodeBooks.message_type,

        "radio_q1": CodeBooks.yes_no_both,
        "radio_q2": CodeBooks.yes_no_both,
        "radio_q5": CodeBooks.yes_no_both
    }
    for td in all_messages:
        CodeBooks.apply(user, code_books, td)

        # Map missing data in radio show columns to a code while keeping raw non-missing data
        x = ["age_clean", "raw_radio_q1", "raw_radio_q2", "raw_radio_q3", "raw_radio_q4", "raw_radio_q5"]
        for keys in all_show_keys.values():
            x.extend(keys)
        x.extend(trustworthy_advisors_keys)
        x.extend(outbreak_keys)
        code_book_data = dict()
        for key in x:
            code_book_data[key] = CodeBooks.apply_missing_code_book(td.get(key))
        td.append_data(code_book_data, Metadata(user, Metadata.get_call_location(), time.time()))

    output_keys = [
        "date_time",
        "date_time_raw",
        "phone_uuid",

        "district_clean",
        "district_raw",
        "urban_rural_clean",
        "urban_rural_raw",
        "gender_clean",
        "gender_raw",

        "radio_station_clean",
        "radio_station_raw",
        "age_clean",
        "age_raw",
        "education_clean",
        "education_raw",
        "idp_clean",
        "idp_raw",
        "origin_district_clean",
        "origin_district_raw",

        "household_sickness_clean",
        "sickness_adult_child",
        "household_sickness_raw",
        "cholera_vaccination_clean",
        "cholera_vaccination_raw",
    ]
    output_keys.extend(trustworthy_advisors_keys)
    output_keys.extend(outbreak_keys)
    output_keys.append("trustworthy_advisors_raw")
    output_keys.extend([
        "radio_show",
        "message_type",

        "raw_radio_q1",
        "raw_radio_q2",
        "raw_radio_q3",
        "raw_radio_q4",
        "raw_radio_q5",

        "radio_q1",
        "radio_q2",
        "radio_q5"
    ])
    for show_keys in all_show_keys.values():
        show_keys = list(show_keys)
        show_keys.sort()
        output_keys.extend(show_keys)

    # Determine consent
    print("Consent")
    print("  Total Respondents:")
    print("  " + str(len({td["phone_uuid"] for td in all_messages})))
    print("  Stopped Respondents:")
    stopped_ids = set()
    for td in all_messages:
        stop_d = dict()
        for output_key in output_keys:
            if td[output_key] == "stop":
                stopped_ids.add(td["phone_uuid"])
                for k in output_keys:
                    stop_d[k] = "stop"
                stop_d["consent_clean"] = CodeBooks.yes_no[Codes.NO]
        if "consent_clean" not in stop_d:
            stop_d["consent_clean"] = CodeBooks.yes_no[Codes.YES]
        td.append_data(stop_d, Metadata(user, Metadata.get_call_location(), time.time()))
    print("  " + str(len(stopped_ids)))

    output_keys.insert(2, "consent_clean")

    # Output analysis TracedData to JSON
    IOUtils.ensure_dirs_exist_for_file(json_output_path)
    with open(json_output_path, "w") as f:
        TracedDataJsonIO.export_traced_data_iterable_to_json(all_messages, f, pretty_print=True)

    # Output analysis file as CSV
    IOUtils.ensure_dirs_exist_for_file(csv_output_path)
    with open(csv_output_path, "w") as f:
        TracedDataCSVIO.export_traced_data_iterable_to_csv(all_messages, f, output_keys)
