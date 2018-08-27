import argparse
import time
from os import path

import pytz as pytz
from core_data_modules.cleaners import Codes
from core_data_modules.traced_data import TracedData, Metadata
from core_data_modules.traced_data.io import TracedDataJsonIO, TracedDataCSVIO
from core_data_modules.util import IOUtils
from dateutil.parser import isoparse

from code_books import CodeBooks

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
            return Codes.NOT_CODED
        if total_matches > 1:
            print("Warning: '{}' matches multiple promos, adverts, and/or shows".format(iso_date))
            return Codes.NOT_CODED

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
        elif show_number == 5:
            return message_type(td["S06E05_Water_Quality (Time) - wt_s06e05_activation"])


    def aggregate_messages(td_1, td_2):
        new_d = dict()

        same_keys = [
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

            # "radio_q1",
            # "radio_q2"
        ]

        for key in same_keys:
            assert td_1[key] == td_2[key], "Key '{}' has conflicting values: '{}' vs '{}'".format(key, td_1[key], td_2[key])
            new_d[key] = td_1[key]

        same_keys.extend([
            "date_time",
            "raw_radio_q1",
            "raw_radio_q2",
            "raw_radio_q3",
            "raw_radio_q4",
            "raw_radio_q5",
            "message_type",
            "radio_show",

            "radio_q1",
            "radio_q2"
        ])

        if "raw_radio_q1" in td_1 and "raw_radio_q1" in td_2:
            new_d["date_time"] = td_1["date_time"][0:10]
            new_d["raw_radio_q1"] = "{};{}".format(td_1["raw_radio_q1"], td_2["raw_radio_q1"])
        elif "raw_radio_q2" in td_1 and "raw_radio_q2" in td_2:
            new_d["date_time"] = td_1["date_time"][0:10]
            new_d["raw_radio_q2"] = "{};{}".format(td_1["raw_radio_q2"], td_2["raw_radio_q2"])
        else:
            new_d["date_time"] = td_1["date_time"]

        if td_1.get("radio_q1") == "stop" or td_2.get("radio_q1") == "stop":
            new_d["radio_q1"] = "stop"
        else:
            new_d["radio_q1"] = td_1.get("radio_q1") if td_1.get("radio_q1") == td_2.get("radio_q1") else "NL"

        if td_1.get("radio_q2") == "stop" or td_2.get("radio_q2") == "stop":
            new_d["radio_q2"] = "stop"
        else:
            new_d["radio_q2"] = td_1.get("radio_q2") if td_1.get("radio_q2") == td_2.get("radio_q2") else "NL"

        if td_1["message_type"] != td_2["message_type"]:
            new_d["message_type"] = "NC"

        if td_1["radio_show"] != td_2["radio_show"]:
            new_d["radio_show"] = "NC"

        for key in td_1:
            if key.startswith("radio_q1_yes_") or key.startswith("radio_q1_no_") or \
                    key.startswith("radio_q2_yes_") or key.startswith("radio_q2_no_"):
                new_d[key] = "1" if td_1[key] == "1" or td_2[key] == "1" else "0"
                same_keys.append(key)
            if key not in same_keys:
                new_d[key] = "PRE_MERGE_UNIFICATION"

        td_out = td_1.copy()
        td_out.append_data(new_d, Metadata(user, Metadata.get_call_location(), time.time()))
        return td_out


    # Load surveys
    with open(survey_input_path, "r") as f:
        surveys = TracedDataJsonIO.import_json_to_traced_data_iterable(f)

    shows = {
        1: "wt_s06e1_activation",
        2: "wt_s06e2_activation",
        # 3: "wt_s06e03_activation",
        # 4: "wt_s06e04_activation",
        # 5: "wt_s06e05_activation"
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
    for show_number, show_name in shows.items():
        show_messages = load_show(show_name)
        TracedData.update_iterable(user, "avf_phone_id", show_messages, surveys, "surveys")

        for td in show_messages:
            td.append_data({
                "date_time_utc": isoparse(td["created_on"]).strftime("%Y-%m-%d %H:%M"),
                "date_time":
                    isoparse(td["created_on"]).astimezone(pytz.timezone("Africa/Nairobi")).strftime("%Y-%m-%d %H:%M"),
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
                coded_shows_prefix = "S06E01_Risk_Perception (Text) - wt_s06e1_activation_coded_"
                yes_no_key = "{}yes_no".format(coded_shows_prefix)
                yes_prefix = "radio_q1_yes_"
                no_prefix = "radio_q1_no_"
            elif show_number == 2:
                coded_shows_prefix = "S06E02_Cholera_Preparedness (Text) - wt_s06e2_activation_coded_"
                yes_no_key = "{}yes_no".format(coded_shows_prefix)
                yes_prefix = "radio_q2_yes_"
                no_prefix = "radio_q2_no_"
            else:
                assert False

            d = dict()
            yes_no = td[yes_no_key]
            d["radio_q{}".format(show_number)] = yes_no
            for output_key in td:
                if output_key.startswith(coded_shows_prefix) and output_key != yes_no_key:
                    code_yes_key = output_key.replace(coded_shows_prefix, yes_prefix)
                    code_no_key = output_key.replace(coded_shows_prefix, no_prefix)
                    all_show_keys[show_number].update({code_yes_key, code_no_key})

                    if yes_no == Codes.YES:
                        d[code_yes_key] = td[output_key]
                        d[code_no_key] = "0"  # "NC"
                    elif yes_no == Codes.NO:
                        d[code_yes_key] = "0"
                        d[code_no_key] = td[output_key]
                    else:
                        d[code_yes_key] = "0"
                        d[code_no_key] = "0"

            td.append_data(d, Metadata(user, Metadata.get_call_location(), time.time()))

        all_messages.extend(show_messages)

    # Set keys to other shows to NS
    for td in all_messages:
        ns_show_answers = dict()
        for show_number, show_keys in all_show_keys.items():
            if td["raw_radio_q{}".format(show_number)] == Codes.SKIPPED:
                ns_show_answers["radio_q{}".format(show_number)] = Codes.SKIPPED
                for output_key in show_keys:
                    ns_show_answers[output_key] = "0"  # Codes.SKIPPED
        td.append_data(ns_show_answers, Metadata(user, Metadata.get_call_location(), time.time()))

    # Group input messages by participant/day
    lut = dict()  # of [avf_phone_id, date] -> (list of TracedData)
    for td in all_messages:
        key = (td["phone_uuid"], isoparse(td["date_time"]).strftime("%Y-%m-%d"))
        if key not in lut:
            lut[key] = []
        lut[key].append(td)

    collated_messages = []
    for messages in lut.values():
        out = messages.pop(0)
        while len(messages) > 0:
            out = aggregate_messages(out, messages.pop(0))
        collated_messages.append(out)

    print("A")
    print(len(all_messages))
    print(len(collated_messages))

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
        "cholera_vaccination_clean": CodeBooks.yes_no,
        # "trustworthy_advisors_clean": TODO

        "message_type": CodeBooks.message_type,

        "radio_q1": CodeBooks.yes_no,
        "radio_q2": CodeBooks.yes_no,
        # TODO: Other radio show questions
    }
    for td in all_messages:
        CodeBooks.apply(user, code_books, td)

        # Map missing data in radio show columns to a code while keeping raw non-missing data
        x = ["age_clean", "raw_radio_q1", "raw_radio_q2", "raw_radio_q3", "raw_radio_q4", "raw_radio_q5"]
        # for keys in all_show_keys.values():
        #     x.extend(keys)
        code_book_data = dict()
        for key in x:
            code_book_data[key] = CodeBooks.apply_missing_code_book(td[key])
        td.append_data(code_book_data, Metadata(user, Metadata.get_call_location(), time.time()))

    output_keys = [
        "date_time",
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
        "raw_radio_q5",

        "radio_q1",
        "radio_q2"
    ]
    for show_keys in all_show_keys.values():
        show_keys = list(show_keys)
        show_keys.sort()
        output_keys.extend(show_keys)

    # Determine consent
    print("Total Respondents:")
    print(len({td["phone_uuid"] for td in all_messages}))
    print("Stopped Respondents:")
    stopped_ids = set()
    for td in all_messages:
        stopped_updates = dict()
        for output_key in output_keys:
            if td[output_key] == "stop":
                stopped_ids.add(td["phone_uuid"])
                for k in output_keys:
                    stopped_updates[k] = "stop"
                stopped_updates["consent_clean"] = CodeBooks.yes_no[Codes.NO]
        if "consent_clean" not in stopped_updates:
            stopped_updates["consent_clean"] = CodeBooks.yes_no[Codes.YES]
        td.append_data(stopped_updates, Metadata(user, Metadata.get_call_location(), time.time()))
    print(len(stopped_ids))

    output_keys.insert(2, "consent_clean")

    # Output analysis TracedData to JSON
    IOUtils.ensure_dirs_exist_for_file(json_output_path)
    with open(json_output_path, "w") as f:
        TracedDataJsonIO.export_traced_data_iterable_to_json(all_messages, f, pretty_print=True)

    # Output analysis file as CSV
    IOUtils.ensure_dirs_exist_for_file(csv_output_path)
    with open(csv_output_path, "w") as f:
        TracedDataCSVIO.export_traced_data_iterable_to_csv(all_messages, f, output_keys)
