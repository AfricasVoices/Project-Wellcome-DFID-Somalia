import argparse
import os
import time
from collections import namedtuple
from os import path

from core_data_modules.traced_data import Metadata
from core_data_modules.traced_data.io import TracedDataJsonIO, TracedDataCodaIO, TracedDataCodingCSVIO
from core_data_modules.util import IOUtils

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merges manually cleaned files back into a traced data file.")
    parser.add_argument("user", help="User launching this program, for use by TracedData Metadata")
    parser.add_argument("json_input_path", metavar="json-input-path",
                        help="Path to JSON input file, which contains a list of TracedData objects")
    parser.add_argument("coded_input_path", metavar="coded-input-path",
                        help="Directory to read coding files from")
    parser.add_argument("json_output_path", metavar="json-output-path",
                        help="Path to a JSON file to write merged results to")

    args = parser.parse_args()
    user = args.user
    json_input_path = args.json_input_path
    coded_input_path = args.coded_input_path
    json_output_path = args.json_output_path

    # TODO: Refactor into a class before putting this code into the template library
    MergePlan = namedtuple("MergePlane", ["coda_filename", "key_of_raw", "scheme_keys"])

    def make_standard_merge_plan(variable_name, survey_name):
        coda_filename = "{}_coded.csv".format(variable_name)
        key_of_raw = "{} (Text) - {}".format(variable_name, survey_name)
        key_of_coded = "{} (Text) - {}_coded".format(variable_name, survey_name)

        return MergePlan(coda_filename, key_of_raw, {variable_name: key_of_coded})

    merge_plans = [
        make_standard_merge_plan("District", "wt_demog_1"),
        make_standard_merge_plan("Gender", "wt_demog_1"),
        make_standard_merge_plan("Urban_Rural", "wt_demog_1"),

        make_standard_merge_plan("Radio_Station", "wt_demog_2"),
        make_standard_merge_plan("Age", "wt_demog_2"),
        make_standard_merge_plan("Education_Level", "wt_demog_2"),
        make_standard_merge_plan("Idp", "wt_demog_2"),
        make_standard_merge_plan("Origin_District", "wt_demog_2"),

        make_standard_merge_plan("Cholera_Vaccination", "wt_practice"),
        MergePlan("Household_Sickness_coded.csv", "Household_Sickness (Text) - wt_practice",
                  {
                     "Household_Sickness": "Household_Sickness (Text) - wt_practice_coded",
                     "People": "Household_Sickness (Text) - wt_practice_coded_people"
                 }),
        make_standard_merge_plan("Trustworthy_Advisors", "wt_practice")
    ]

    # Load data from JSON file
    with open(json_input_path, "r") as f:
        surveys = TracedDataJsonIO.import_json_to_traced_data_iterable(f)
        
    # Merge manually coded Coda files into the cleaned dataset
    for plan_item in merge_plans:
        coda_file_path = path.join(coded_input_path, plan_item.coda_filename)

        if not path.exists(coda_file_path):
            print("Warning: Coda file '{}' not found".format(plan_item.coda_filename))
            for td in surveys:
                for td_col in plan_item.scheme_keys.values():
                    td.append_data(
                        {td_col: None},
                        Metadata(user, Metadata.get_call_location(), time.time())
                    )
            continue

        with open(coda_file_path, "r") as f:
            TracedDataCodaIO.import_coda_to_traced_data_iterable(
                user, surveys, plan_item.key_of_raw, plan_item.scheme_keys, f, True)

    # Write coded data back out to disk
    IOUtils.ensure_dirs_exist_for_file(json_output_path)
    with open(json_output_path, "w") as f:
        TracedDataJsonIO.export_traced_data_iterable_to_json(surveys, f, pretty_print=True)
