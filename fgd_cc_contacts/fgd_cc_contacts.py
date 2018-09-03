import argparse
import time

from core_data_modules.cleaners import Codes
from core_data_modules.traced_data import Metadata, TracedData
from core_data_modules.traced_data.io import TracedDataJsonIO, TracedDataCSVIO
from core_data_modules.util import IOUtils

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cleans the wt surveys and exports variables to Coda for "
                                                 "manual verification and coding")
    parser.add_argument("user", help="User launching this program, for use by TracedData Metadata")
    parser.add_argument("phone_uuid_table_path", metavar="phone-uuid-table-path",
                        help="JSON file containing an existing phone number <-> UUID lookup table. ")
    parser.add_argument("fgd_cc_input_path", metavar="fgd-cc-input-path",
                        help="Path to input file, containing a list of serialized TracedData objects as JSON")
    parser.add_argument("demog_surveys_input_path", metavar="demog-surveys-input-path",
                        help="Path to input file, containing a list of serialized TracedData objects as JSON")
    parser.add_argument("json_output_path", metavar="json-output-path",
                        help="Path to a JSON file to write processed TracedData messages to")
    parser.add_argument("contacts_csv_output_path", metavar="contacts-csv-output-path",
                        help="Path to a CSV file to write FGD/CC contacts to")

    args = parser.parse_args()
    user = args.user
    phone_uuid_table_path = args.phone_uuid_table_path
    fgd_cc_input_path = args.fgd_cc_input_path
    demog_surveys_input_path = args.demog_surveys_input_path
    json_output_path = args.json_output_path
    contacts_csv_output_path = args.contacts_csv_output_path

    # Load FGD/CC survey responses
    with open(fgd_cc_input_path, "r") as f:
        fgd_cc_data = TracedDataJsonIO.import_json_to_traced_data_iterable(f)

    # Load coded demog surveys
    with open(demog_surveys_input_path, "r") as f:
        surveys = TracedDataJsonIO.import_json_to_traced_data_iterable(f)

    # Filter out people who haven't answered the fgd_cc consent question
    fgd_cc_consent_key = "Response_1 (Category) - wt_fgd_cc"
    fgd_cc_data = [td for td in fgd_cc_data if fgd_cc_consent_key in td]

    # Apply the demog surveys to the fgd_cc data
    TracedData.update_iterable(user, "avf_phone_id", fgd_cc_data, surveys, "surveys")

    # Annotate fgd_cc_data with whether or not the respondent's district is Mogadishu
    raw_district_key = "District (Text) - wt_demog_1"
    coded_district_key = "District (Text) - wt_demog_1_coded"
    raw_age_key = "Age (Text) - wt_demog_2"
    coded_age_key = "Age (Text) - wt_demog_2_coded"
    for td in fgd_cc_data:
        if raw_district_key not in td:
            td.append_data({
                raw_district_key: "NA"
            }, Metadata(user, Metadata.get_call_location(), time.time()))

        if coded_district_key not in td:
            td.append_data({
                coded_district_key: "none"
            }, Metadata(user, Metadata.get_call_location(), time.time()))

        is_mogadishu = td[coded_district_key] == "mogadishu" or td[coded_district_key] == "mogadisho"
        td.append_data({
            "Raw FGD/CC Response": td["Response_1 (Text) - wt_fgd_cc"],
            "FGD/CC Consented": td[fgd_cc_consent_key],
            "Raw District": td[raw_district_key],
            "Coded District":
                td[coded_district_key] if td[raw_district_key] != Codes.TRUE_MISSING else Codes.TRUE_MISSING,
            "Coded Age": td[coded_age_key] if td[raw_age_key] != Codes.TRUE_MISSING else Codes.TRUE_MISSING,
            "District Mogadishu": "Yes" if is_mogadishu else "No",
            "FGD/CC Consented and District Mogadishu":
                "Yes" if is_mogadishu and td[fgd_cc_consent_key] == "Yes" else "No"
        }, Metadata(user, Metadata.get_call_location(), time.time()))

    # Write json output
    IOUtils.ensure_dirs_exist_for_file(json_output_path)
    with open(json_output_path, "w") as f:
        TracedDataJsonIO.export_traced_data_iterable_to_json(fgd_cc_data, f, pretty_print=True)

    # Output to contacts csv
    headers = [
        "avf_phone_id",
        "Raw FGD/CC Response",
        "FGD/CC Consented",
        "Raw District",
        "Coded District",
        "Coded Age",
        "District Mogadishu",
        "FGD/CC Consented and District Mogadishu"
    ]
    with open(contacts_csv_output_path, "w") as f:
        TracedDataCSVIO.export_traced_data_iterable_to_csv(fgd_cc_data, f, headers)
