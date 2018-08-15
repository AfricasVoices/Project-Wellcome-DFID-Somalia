import argparse
import csv
from os import path

from core_data_modules.cleaners import Codes
from core_data_modules.traced_data.io import TracedDataJsonIO
from core_data_modules.util import IOUtils

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

    survey_keys = {
        "District (Text) - wt_demog_1": surveys,
        "Gender (Text) - wt_demog_1": surveys,
        "Urban_Rural (Text) - wt_demog_1": surveys,

        "Radio_Station (Text) - wt_demog_2": surveys,
        "Age (Text) - wt_demog_2": surveys,
        "Education_Level (Text) - wt_demog_2": surveys,
        "Idp (Text) - wt_demog_2": surveys,
        "Origin_District (Text) - wt_demog_2": surveys,

        "Cholera_Vaccination (Text) - wt_practice": surveys,
        "Household_Sickness (Text) - wt_practice": surveys,
        "Trustworthy_Advisors (Text) - wt_practice": surveys
    }

    shows = {
        "S06E01_Risk_Perception (Text) - wt_s06e1_activation": "wt_s06e1_activation",
        "S06E02_Cholera_Preparedness (Text) - wt_s06e2_activation": "wt_s06e2_activation",
        "S06E03_Outbreak_Knowledge (Text) - wt_s06e03_activation": "wt_s06e03_activation",
        "S06E04_Cholera_Recurrency (Text) - wt_s06e04_activation": "wt_s06e04_activation"
    }
    show_keys = {question_key: load_show(show_name) for question_key, show_name in shows.items()}

    keys = dict(show_keys)
    keys.update(survey_keys)

    # Generate survey stats
    stats = []
    for key, data in keys.items():
        clean_key = "{}_clean".format(key)
        coded_key = "{}_coded".format(key)

        def codes_agree(td):
            if not(clean_key in td and coded_key in td):
                return False
            if td[clean_key] == Codes.NOT_CODED:
                return td[coded_key] == "NC"  # TODO: Temporary measure until we update Codes.NOT_CODED in Core Data
            return td[clean_key] == td[coded_key]

        responses = [td for td in data if key in td and td[key] != Codes.TRUE_MISSING]
        auto_coded = [td for td in responses if clean_key in td and td[clean_key] != Codes.NOT_CODED]  # (Note that NOT_CODED is acceptable here because this is internal to the pipeline)
        manually_reviewed = [td for td in responses if coded_key in td and td[coded_key] is not None]
        manually_coded = [td for td in responses
                          if coded_key in td and td[coded_key] is not None and td[coded_key] != "NC"]
        agreeing_codes = [td for td in responses if codes_agree(td)]

        stats.append({
            "Variable": key,
            "Total Respondents": len({td["avf_phone_id"] for td in responses}),
            "Total Messages":  sum([len(td.get_history(key)) for td in responses]),
            "Automatically Coded (%)": "{0:0.1f}".format(len(auto_coded) / len(responses) * 100),
            "Manually Reviewed (%)": "{0:0.1f}".format(len(manually_reviewed) / len(responses) * 100),
            "Manually Verified/Coded (%)": "{0:0.1f}".format(len(manually_coded) / len(responses) * 100),
            "Auto/Manual Agreement (%)": "{0:0.1f}".format(len(agreeing_codes) / len(responses) * 100)
        })

    # Save survey stats
    IOUtils.ensure_dirs_exist_for_file(csv_output_path)
    with open(csv_output_path, "w") as f:
        headers = ["Variable", "Total Respondents", "Total Messages", "Automatically Coded (%)",
                   "Manually Reviewed (%)", "Manually Verified/Coded (%)", "Auto/Manual Agreement (%)"]
        writer = csv.DictWriter(f, fieldnames=headers, lineterminator="\n")
        writer.writeheader()
        for row in stats:
            writer.writerow(row)
