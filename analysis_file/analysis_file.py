import argparse
import time
from os import path

import pytz as pytz
from core_data_modules.cleaners import Codes
from core_data_modules.traced_data import TracedData, Metadata
from core_data_modules.traced_data.io import TracedDataJsonIO, TracedDataCSVIO
from core_data_modules.util import IOUtils
from dateutil.parser import isoparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Summarises response rates/coding rates for surveys")
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

    def get_code(td, key_of_raw, key_of_coded=None):
        if key_of_coded is None:
            key_of_coded = "{}_coded".format(key_of_raw)

        if td[key_of_raw] == Codes.TRUE_MISSING:
            return Codes.TRUE_MISSING
        else:
            return td[key_of_coded]


    def get_origin_district(td):
        if get_code(td, "Idp (Text) - wt_demog_2") == "No":  # TODO: Change to Codes.NO once recoded.
            return Codes.SKIPPED
        else:
            return get_code(td, "Origin_District (Text) - wt_demog_2")


    def message_type(iso_date):
        dt = isoparse(iso_date)

        promo_dates = [
            ["2018-07-22T06:25:00+03:00", "2018-07-23T00:00:00+03:00"],
            ["2018-07-23T00:00:00+03:00", "2018-07-24T00:00:00+03:00"],
            ["2018-07-24T00:00:00+03:00", "2018-07-25T00:00:00+03:00"],
            ["2018-07-25T00:00:00+03:00", "2018-07-26T00:00:00+03:00"],
            ["2018-07-26T00:00:00+03:00", "2018-07-26T19:00:00+03:00"],

            ["2018-07-29T06:25:00+03:00", "2018-07-30T00:00:00+03:00"],
            ["2018-07-30T00:00:00+03:00", "2018-07-31T00:00:00+03:00"],
            ["2018-07-31T00:00:00+03:00", "2018-08-01T00:00:00+03:00"],
            ["2018-08-01T00:00:00+03:00", "2018-08-02T00:00:00+03:00"],
            ["2018-08-02T00:00:00+03:00", "2018-08-02T19:00:00+03:00"],

            ["2018-08-05T06:25:00+03:00", "2018-08-06T00:00:00+03:00"],
            ["2018-08-06T00:00:00+03:00", "2018-08-07T00:00:00+03:00"],
            ["2018-08-07T00:00:00+03:00", "2018-08-08T00:00:00+03:00"],
            ["2018-08-08T00:00:00+03:00", "2018-08-09T00:00:00+03:00"],
            ["2018-08-09T00:00:00+03:00", "2018-08-09T19:00:00+03:00"],

            ["2018-08-12T06:25:00+03:00", "2018-08-13T00:00:00+03:00"],
            ["2018-08-13T00:00:00+03:00", "2018-08-14T00:00:00+03:00"],
            ["2018-08-14T00:00:00+03:00", "2018-08-15T00:00:00+03:00"],
            ["2018-08-15T00:00:00+03:00", "2018-08-16T00:00:00+03:00"],
            ["2018-08-16T00:00:00+03:00", "2018-08-16T19:00:00+03:00"],

            ["2018-08-19T06:25:00+03:00", "2018-08-20T00:00:00+03:00"],
            ["2018-08-20T00:00:00+03:00", "2018-08-21T00:00:00+03:00"],
            ["2018-08-21T00:00:00+03:00", "2018-08-22T00:00:00+03:00"],
            ["2018-08-22T00:00:00+03:00", "2018-08-23T00:00:00+03:00"],
            ["2018-08-23T00:00:00+03:00", "2018-08-23T19:00:00+03:00"]
        ]

        advert_dates = [
            ["2018-07-26T19:00:00+03:00", "2018-07-27T00:00:00+03:00"],
            ["2018-07-27T00:00:00+03:00", "2018-07-27T08:30:00+03:00"],

            ["2018-08-02T19:00:00+03:00", "2018-08-03T00:00:00+03:00"],
            ["2018-08-03T00:00:00+03:00", "2018-08-03T08:30:00+03:00"],

            ["2018-08-09T19:00:00+03:00", "2018-08-10T00:00:00+03:00"],
            ["2018-08-10T00:00:00+03:00", "2018-08-10T08:30:00+03:00"],

            ["2018-08-16T19:00:00+03:00", "2018-08-17T00:00:00+03:00"],
            ["2018-08-17T00:00:00+03:00", "2018-08-17T08:30:00+03:00"],

            ["2018-08-23T19:00:00+03:00", "2018-08-24T00:00:00+03:00"],
            ["2018-08-24T00:00:00+03:00", "2018-08-24T08:30:00+03:00"],
        ]

        show_dates = [
            ["2018-07-27T08:30:00+03:00", "2018-07-28T00:00:00+03:00"],
            ["2018-07-28T00:00:00+03:00", "2018-07-29T00:00:00+03:00"],
            ["2018-07-29T00:00:00+03:00", "2018-07-29T06:25:00+03:00"],

            ["2018-08-03T08:30:00+03:00", "2018-08-04T00:00:00+03:00"],
            ["2018-08-04T00:00:00+03:00", "2018-08-05T00:00:00+03:00"],
            ["2018-08-05T00:00:00+03:00", "2018-08-05T06:25:00+03:00"],

            ["2018-08-10T08:30:00+03:00", "2018-08-11T00:00:00+03:00"],
            ["2018-08-11T00:00:00+03:00", "2018-08-12T00:00:00+03:00"],
            ["2018-08-12T00:00:00+03:00", "2018-08-12T06:25:00+03:00"],

            ["2018-08-17T08:30:00+03:00", "2018-08-18T00:00:00+03:00"],
            ["2018-08-18T00:00:00+03:00", "2018-08-19T00:00:00+03:00"],
            ["2018-08-19T00:00:00+03:00", "2018-08-19T06:25:00+03:00"],

            ["2018-08-24T08:30:00+03:00", "2018-08-25T00:00:00+03:00"],
            ["2018-08-25T00:00:00+03:00", "2018-08-26T00:00:00+03:00"],
            ["2018-08-26T00:00:00+03:00", "2018-08-26T06:25:00+03:00"]
        ]

        total_matches = 0
        message_type = ""
        for p in promo_dates:
            if isoparse(p[0]) <= dt < isoparse(p[1]):
                message_type = "promo"
                total_matches += 1

        for a in advert_dates:
            if isoparse(a[0]) <= dt < isoparse(a[1]):
                message_type = "advert"
                total_matches += 1

        for s in show_dates:
            if isoparse(s[0]) <= dt < isoparse(s[1]):
                message_type = "show"
                total_matches += 1

        if total_matches == 0:
            print("Warning: '{}' has no matching promo, advert, or show".format(iso_date))
            return "NL"  # TODO: Change to Codes.NOT_LOGICAL
        if total_matches > 1:
            print("Warning: '{}' matches multiple promos, adverts, and/or shows".format(iso_date))
            return "NL"  # TODO: Change to Codes.NOT_LOGICAL

        return message_type

    def message_type_for_show(show_number, td):
        if show_number == 1:
            return message_type(td["S06E01_Risk_Perception (Time) - wt_s06e1_activation"])
        elif show_number == 2:
            return message_type(td["S06E02_Cholera_Preparedness (Time) - wt_s06e2_activation"])
        elif show_number == 3:
            return message_type(td["S06E03_Outbreak_Knowledge (Time) - wt_s06e03_activation"])
        elif show_number == 4:
            return message_type(td["S06E04_Cholera_Recurrency (Time) - wt_s06e04_activation"])

    # Load surveys
    with open(survey_input_path, "r") as f:
        surveys = TracedDataJsonIO.import_json_to_traced_data_iterable(f)

    shows = {
        1: "wt_s06e1_activation",
        # 2: "wt_s06e2_activation",
        # 3: "wt_s06e03_activation",
        # 4: "wt_s06e04_activation",
        # 5: "wt_s06e05_activation"
    }

    # Produce output columns for each input message
    all_messages = []
    show_1_keys = set()
    for show_number, show_name in shows.items():
        show_messages = load_show(show_name)
        TracedData.update_iterable(user, "avf_phone_id", show_messages, surveys, "surveys")

        for td in show_messages:
            td.append_data({
                "date_time_utc": isoparse(td["created_on"]).strftime("%Y-%m-%d %H:%M"),
                # TODO: Need to think about what to do when collating by date.
                "date_time":
                    isoparse(td["created_on"]).astimezone(pytz.timezone("Africa/Nairobi")).strftime("%Y-%m-%d %H:%M"),
                # "consent_clean": TODO
                "phone_uuid": td["avf_phone_id"],

                "district_clean": get_code(td, "District (Text) - wt_demog_1"),
                "urban_rural_clean": get_code(td, "Urban_Rural (Text) - wt_demog_1"),
                "gender_clean": get_code(td, "Gender (Text) - wt_demog_1"),

                "radio_station_clean": get_code(td, "Radio_Station (Text) - wt_demog_2"),
                "age_clean": get_code(td, "Age (Text) - wt_demog_2"),
                "education_clean": get_code(td, "Education_Level (Text) - wt_demog_2"),
                "idp_clean": get_code(td, "Idp (Text) - wt_demog_2"),
                "origin_district_clean": get_origin_district(td),

                "household_sickness_clean": get_code(td, "Household_Sickness (Text) - wt_practice"),
                "sickness_adult_child": get_code(td, "Household_Sickness (Text) - wt_practice",
                                                 "Household_Sickness (Text) - wt_practice_coded_people"),
                "cholera_vaccination_clean": get_code(td, "Cholera_Vaccination (Text) - wt_practice"),
                "trustworthy_advisors_clean": get_code(td, "Trustworthy_Advisors (Text) - wt_practice"),

                "radio_show": show_number,
                "message_type": message_type_for_show(show_number, td),

                "raw_radio_q1": td.get("S06E01_Risk_Perception (Text) - wt_s06e1_activation", "NS"),
                "raw_radio_q2": td.get("S06E02_Cholera_Preparedness (Text) - wt_s06e2_activation", "NS"),
                "raw_radio_q3": td.get("S06E03_Outbreak_Knowledge (Text) - wt_s06e03_activation", "NS"),
                "raw_radio_q4": td.get("S06E04_Cholera_Recurrency (Text) - wt_s06e04_activation", "NS"),
                "raw_radio_q5": td.get("S06E05_Water_Quality (Text) - wt_s06e05_activation", "NS")
            }, Metadata(user, Metadata.get_call_location(), time.time()))

            if show_number == 1:
                td.append_data({
                    key.replace("S06E01_Risk_Perception (Text) - wt_s06e1_activation_coded_", "radio_q1_"): td[key]
                    for key in td if key.startswith("S06E01_Risk_Perception (Text) - wt_s06e1_activation_coded_")
                }, Metadata(user, Metadata.get_call_location(), time.time()))

                show_1_keys.update(
                    {key.replace("S06E01_Risk_Perception (Text) - wt_s06e1_activation_coded_", "radio_q1_")
                     for key in td if key.startswith("S06E01_Risk_Perception (Text) - wt_s06e1_activation_coded_")})

        all_messages.extend(show_messages)

    # Output analysis TracedData to JSON
    IOUtils.ensure_dirs_exist_for_file(json_output_path)
    with open(json_output_path, "w") as f:
        TracedDataJsonIO.export_traced_data_iterable_to_json(all_messages, f, pretty_print=True)

    # Output analysis file as CSV
    output_keys = [
        "date_time",
        "date_time_utc",
        # "consent_clean", TODO
        "phone_uuid",

        "district_clean",
        "urban_rural_clean",
        "gender_clean",

        "radio_station_clean",
        "age_clean",
        "education_clean",
        "idp_clean",
        "origin_district_clean",

        "household_sickness_clean",
        "sickness_adult_child",
        "cholera_vaccination_clean",
        "trustworthy_advisors_clean",

        "radio_show",
        "message_type",

        "raw_radio_q1",
        "raw_radio_q2",
        "raw_radio_q3",
        "raw_radio_q4",
        "raw_radio_q5"
    ]
    output_keys.extend(show_1_keys)

    IOUtils.ensure_dirs_exist_for_file(csv_output_path)
    with open(csv_output_path, "w") as f:
        TracedDataCSVIO.export_traced_data_iterable_to_csv(all_messages, f, output_keys)
