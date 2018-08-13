import argparse
import csv

from core_data_modules.cleaners import Codes
from core_data_modules.traced_data.io import TracedDataJsonIO
from core_data_modules.util import IOUtils

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Summarises response rates/coding rates for surveys")
    # TODO: Also summarise messages
    parser.add_argument("user", help="User launching this program")
    parser.add_argument("survey_input_path", metavar="survey-input-path",
                        help="Path to a coded survey JSON file, containing a list of serialized TracedData objects")
    parser.add_argument("csv_output_path", metavar="csv-output-path",
                        help="Path to a CSV file to write the summarised stats to")

    args = parser.parse_args()
    user = args.user
    survey_input_path = args.survey_input_path
    csv_output_path = args.csv_output_path

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

    # Load surveys
    with open(survey_input_path, "r") as f:
        surveys = TracedDataJsonIO.import_json_to_traced_data_iterable(f)

    # Generate survey stats
    survey_stats = []
    for key in survey_keys:
        clean_key = "{}_clean".format(key)
        coded_key = "{}_coded".format(key)

        def codes_agree(td):
            if not(clean_key in td and coded_key in td):
                return False

            if td[clean_key] == Codes.NOT_CODED:
                return td[coded_key] == "N/C"  # TODO: Temporary measure until we update Codes.NOT_CODED in Core Data

            return td[clean_key] == td[coded_key]

        responses = [td for td in surveys if key in td and td[key] != Codes.TRUE_MISSING]
        auto_coded = [td for td in responses if clean_key in td and td[clean_key] != Codes.TRUE_MISSING and
                      td[clean_key] != Codes.NOT_CODED]
        manually_coded = [td for td in responses if coded_key in td and td[coded_key] != Codes.TRUE_MISSING and
                          td[coded_key] != Codes.NOT_CODED]
        agreeing_codes = [td for td in responses if codes_agree(td)]

        survey_stats.append({
            "Variable": key,
            "Total Respondents": len(responses),
            "Total Messages": sum([len(td.get_history(key)) for td in responses]),
            "Automatically Coded (%)": "{0:0.1f}".format(len(auto_coded) / len(responses) * 100),
            "Manually Verified/Coded (%)": "{0:0.1f}".format(len(manually_coded) / len(responses) * 100),
            "Auto/Manual Agreement (%)": "{0:0.1f}".format(len(agreeing_codes) / len(responses) * 100)
        })

    # Save survey stats
    IOUtils.ensure_dirs_exist_for_file(csv_output_path)
    with open(csv_output_path, "w") as f:
        headers = ["Variable", "Total Respondents", "Total Messages", "Automatically Coded (%)",
                   "Manually Verified/Coded (%)", "Auto/Manual Agreement (%)"]
        writer = csv.DictWriter(f, fieldnames=headers, lineterminator="\n")
        writer.writeheader()
        for row in survey_stats:
            writer.writerow(row)
