import argparse
import os
import time
from os import path

from core_data_modules.cleaners import somali, Codes
from core_data_modules.traced_data import Metadata
from core_data_modules.traced_data.io import TracedDataJsonIO, TracedDataCodaIO

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cleans the wt surveys and exports variables to Coda for "
                                                 "manual verification and coding")
    parser.add_argument("user", help="User launching this program, for use by TracedData Metadata")
    parser.add_argument("demog_1_input_path", metavar="demog-1-input-path",
                        help="Path to input file, containing a list of serialized TracedData objects as JSON")
    parser.add_argument("demog_2_input_path", metavar="demog-2-input-path",
                        help="Path to input file, containing a list of serialized TracedData objects as JSON")
    parser.add_argument("practice_input_path", metavar="practice-input-path",
                        help="Path to input file, containing a list of serialized TracedData objects as JSON")
    parser.add_argument("json_output_path", metavar="json-output-path",
                        help="Path to a JSON file to write processed TracedData messages to")
    parser.add_argument("coded_output_path", metavar="coding-output-path",
                        help="Directory to write coding files to")

    args = parser.parse_args()
    user = args.user
    demog_1_input_path = args.demog_1_input_path
    demog_2_input_path = args.demog_2_input_path
    practice_input_path = args.practice_input_path
    json_output_path = args.json_output_path
    coded_output_path = args.coded_output_path

    cleaning_plan = {
        "District (Text) - wt_demog_1": somali.DemographicCleaner.clean_somalia_district,
        "Gender (Text) - wt_demog_1": somali.DemographicCleaner.clean_gender,
        "Urban_Rural (Text) - wt_demog_1": somali.DemographicCleaner.clean_urban_rural,

        "Radio_Station (Text) - wt_demog_2": None,
        "Age (Text) - wt_demog_2": somali.DemographicCleaner.clean_age,
        "Education_Level (Text) - wt_demog_2": None,
        "Idp (Text) - wt_demog_2": somali.DemographicCleaner.clean_yes_no,
        "Origin_District (Text) - wt_demog_2": somali.DemographicCleaner.clean_somalia_district,

        "Household_Sickness (Text) - wt_practice": somali.DemographicCleaner.clean_yes_no,
        "Cholera_Vaccination (Text) - wt_practice": somali.DemographicCleaner.clean_yes_no,
        "Trustworthy_Advisors (Text) - wt_practice": None
    }

    # Load data from JSON file
    with open(demog_1_input_path, "r") as f:
        demog_1_data = TracedDataJsonIO.import_json_to_traced_data_iterable(f)
    with open(demog_2_input_path, "r") as f:
        demog_2_data = TracedDataJsonIO.import_json_to_traced_data_iterable(f)
    with open(practice_input_path, "r") as f:
        practice_data = TracedDataJsonIO.import_json_to_traced_data_iterable(f)

    def join_traced_data_iterables(join_on_key, data1, data2):
        # TODO: Move to CoreDataModules
        """
        Outer-joins two iterables of TracedData on the given key.

        :param join_on_key: Key to join data on
        :type join_on_key: str
        :param data1: TracedData items to join with data2
        :type data1: iterable of TracedData
        :param data2: TracedData items to join with data1
        :type data2: iterable of TracedData
        :return: data1 outer-joined with data2 on join_on_key
        :rtype: list of TracedData
        """
        data_1_lut = {td[join_on_key]: td for td in data1}
        data_2_lut = {td[join_on_key]: td for td in data2}

        ids_in_data1_only = data_1_lut.keys() - data_2_lut.keys()
        ids_in_data2_only = data_2_lut.keys() - data_1_lut.keys()
        ids_in_both = set(data_1_lut.keys()).intersection(set(data_2_lut.keys()))

        merged_data = []
        for id in ids_in_data1_only:
            merged_data.append(data_1_lut[id])
        for id in ids_in_data2_only:
            merged_data.append(data_2_lut[id])
        for id in ids_in_both:
            # TODO: Preserve history from both trees.
            # TODO: Assert all keys in common between the two TracedData items here have identical values.
            data_1_lut[id].append_data(
                dict(data_2_lut[id].items()),
                Metadata(user, Metadata.get_call_location(), time.time())
            )
            merged_data.append(data_1_lut[id])

        return merged_data

    demog_data = join_traced_data_iterables("avf_phone_id", demog_1_data, demog_2_data)
    all_survey_data = join_traced_data_iterables("avf_phone_id", demog_data, practice_data)

    # Clean the survey responses
    for td in all_survey_data:
        for key, cleaner in cleaning_plan.items():
            if cleaner is not None and key in td:
                td.append_data(
                    {"{}_clean".format(key): cleaner(td[key])},
                    Metadata(user, Metadata.get_call_location(), time.time())
                )

    # Mark missing entries in the raw data as true missing
    for td in all_survey_data:
        for key in cleaning_plan:
            if key not in td:
                td.append_data({key: Codes.TRUE_MISSING}, Metadata(user, Metadata.get_call_location(), time.time()))

    # Write json output
    if os.path.dirname(json_output_path) is not "" and not os.path.exists(os.path.dirname(json_output_path)):
        os.makedirs(os.path.dirname(json_output_path))
    with open(json_output_path, "w") as f:
        TracedDataJsonIO.export_traced_data_iterable_to_json(all_survey_data, f, pretty_print=True)

    # Output for manual verification + coding
    if not os.path.exists(coded_output_path):
        os.makedirs(coded_output_path)

    # TODO: Tidy up the usage of keys here once the format of the keys has been updated.
    for key in cleaning_plan.keys():
        output_file_path = path.join(coded_output_path, "{}.csv".format(key.split(" ")[0]))
        with open(output_file_path, "w") as f:
            TracedDataCodaIO.export_traced_data_iterable_to_coda_with_scheme(
                all_survey_data, key, "{}_clean".format(key), key.split(" ")[0], f)
