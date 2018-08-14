import argparse
import csv
import time
from os import path

from core_data_modules.cleaners import Codes
from core_data_modules.traced_data import TracedData, Metadata
from core_data_modules.traced_data.io import TracedDataJsonIO, TracedDataCSVIO
from core_data_modules.util import IOUtils
from dateutil.parser import isoparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Summarises response rates/coding rates for surveys")
    parser.add_argument("user", help="User launching this program")
    parser.add_argument("messages_input_path", metavar="messages-input-path",
                        help="Path to a directory containing JSON files of responses to each of the shows in this "
                             "project. Each JSON file should contain a list of serialized TracedData objects")
    parser.add_argument("survey_input_path", metavar="survey-input-path",
                        help="Path to a coded survey JSON file, containing a list of serialized TracedData objects")
    parser.add_argument("csv_output_path", metavar="csv-output-path",
                        help="Path to a CSV file to write the summarised stats to")

    args = parser.parse_args()
    user = args.user
    messages_input_path = args.messages_input_path
    survey_input_path = args.survey_input_path
    csv_output_path = args.csv_output_path

    # Load surveys
    with open(survey_input_path, "r") as f:
        surveys = TracedDataJsonIO.import_json_to_traced_data_iterable(f)

    def load_show(show_name):
        show_path = path.join(messages_input_path, "{}.json".format(show_name))
        if not path.exists(show_path):
            print("Warning: No show found with file name '{}.json'".format(show_name))
            return []
        with open(show_path, "r") as f:
            return list(TracedDataJsonIO.import_json_to_traced_data_iterable(f))


    shows = [
        # "wt_s06e1_activation",
        # "wt_s06e2_activation",
        # "wt_s06e03_activation",
        "wt_s06e04_activation"
    ]

    all_messages = []
    for show in shows:
        all_messages.extend(load_show(show))

    TracedData.update_iterable(user, "avf_phone_id", all_messages, surveys, "surveys")

    def get_code(td, variable):
        if td[variable] == Codes.TRUE_MISSING:
            return Codes.TRUE_MISSING
        else:
            return td["{}_coded".format(variable)]

    for td in all_messages:
        td.append_data({
            "date_time": isoparse(td["created_on"]).strftime("%Y-%m-%d %H:%M"),  # TODO: Need to think about what to do when collating by date. Also need to consider converting to EAT.
            # "consent_clean": TODO
            "phone_uuid": td["avf_phone_id"],

            "district_clean": get_code(td, "District (Text) - wt_demog_1"),
            "urban_rural_clean": get_code(td, "Urban_Rural (Text) - wt_demog_1"),
            "gender_clean": get_code(td, "Gender (Text) - wt_demog_1"),

            "radio_station_clean": get_code(td, "Radio_Station (Text) - wt_demog_2"),
            "age_clean": get_code(td, "Age (Text) - wt_demog_2"),
            "education_clean": get_code(td, "Education_Level (Text) - wt_demog_2"),
            "idp_clean": get_code(td, "Idp (Text) - wt_demog_2"),
            "origin_district": get_code(td, "Origin_District (Text) - wt_demog_2"),

            "household_sickness_clean": get_code(td, "Household_Sickness (Text) - wt_practice"),
            # "sickness_adult_child": TODO
            "cholera_vaccination_clean": get_code(td, "Cholera_Vaccination (Text) - wt_practice"),
            "trustworthy_advisors_clean": get_code(td, "Trustworthy_Advisors (Text) - wt_practice"),

            # "radio_show": TODO
        }, Metadata(user, Metadata.get_call_location(), time.time()))

    with open(csv_output_path, "w") as f:
        TracedDataCSVIO.export_traced_data_iterable_to_csv(
            all_messages, f,
            [
                "date_time",
                # "consent_clean", TODO
                "phone_uuid",

                "district_clean",
                "urban_rural_clean",
                "gender_clean",

                "radio_station_clean",
                "age_clean",
                "education_clean",
                "idp_clean",
                "origin_district",

                "household_sickness_clean",
                "cholera_vaccination_clean",
                "trustworthy_advisors_clean"
            ]
        )

    # survey_keys = {
    #     "Cholera_Vaccination (Text) - wt_practice": surveys,
    #     "Household_Sickness (Text) - wt_practice": surveys,
    #     "Trustworthy_Advisors (Text) - wt_practice": surveys
    # }
    #
    # shows = {
    #     "S06E01_Risk_Perception (Text) - wt_s06e1_activation": "wt_s06e1_activation",
    #     "S06E02_Cholera_Preparedness (Text) - wt_s06e2_activation": "wt_s06e2_activation",
    #     "S06E03_Outbreak_Knowledge (Text) - wt_s06e03_activation": "wt_s06e03_activation",
    #     "S06E04_Cholera_Recurrency (Text) - wt_s06e04_activation": "wt_s06e04_activation"
    # }
    # show_keys = {question_key: load_show(show_name) for question_key, show_name in shows.items()}
    #
    # keys = dict(show_keys)
    # keys.update(survey_keys)


