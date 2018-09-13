import argparse
import random
import time

from core_data_modules.cleaners import Codes
from core_data_modules.traced_data import Metadata, TracedData
from core_data_modules.traced_data.io import TracedDataJsonIO, TracedDataCSVIO
from core_data_modules.util import IOUtils, PhoneNumberUuidTable

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
    parser.add_argument("fgd_csv_output_path", metavar="fgd-csv-output-path",
                        help="Path to a CSV file to write 160 call centre contacts to")
    parser.add_argument("cc_csv_output_path", metavar="cc-csv-output-path",
                        help="Path to a CSV file to write 40 gender-balanced focus group discussion contacts to")

    args = parser.parse_args()
    user = args.user
    phone_uuid_table_path = args.phone_uuid_table_path
    fgd_cc_input_path = args.fgd_cc_input_path
    demog_surveys_input_path = args.demog_surveys_input_path
    json_output_path = args.json_output_path
    fgd_csv_output_path = args.fgd_csv_output_path
    cc_csv_output_path = args.cc_csv_output_path

    MINIMUM_AGE = 18
    TOTAL_CC_CONTACTS = 160
    TOTAL_FGD_CONTACTS = 40

    # Load phone uuid table
    with open(phone_uuid_table_path, "r") as f:
        phone_uuids = PhoneNumberUuidTable.load(f)

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

    # Annotate fgd_cc_data with whether or not the respondent's is from Mogadishu
    mogadishu_districts = [
        "mogadishu",
        "mogadisho",  # TODO: Remove need for this by correcting Coda file
        "boondheere",
        "cabdiasis",
        "daynile",
        "dharkenley",
        "heliwa",
        "hodan",
        "hawl wadaag",
        "karaan",
        "shangaani",
        "shibis",
        "waaberi",
        "wadajir",
        "wardhiigleey",
        "xamar jajab",
        "xamar weyn",
        "yaaqshid"
    ]
    raw_district_key = "District (Text) - wt_demog_1"
    coded_district_key = "District (Text) - wt_demog_1_coded"
    raw_age_key = "Age (Text) - wt_demog_2"
    coded_age_key = "Age (Text) - wt_demog_2_coded"
    raw_gender_key = "Gender (Text) - wt_demog_1"
    coded_gender_key = "Gender (Text) - wt_demog_1_coded"
    for td in fgd_cc_data:
        if raw_district_key not in td:
            td.append_data({
                raw_district_key: "NA"
            }, Metadata(user, Metadata.get_call_location(), time.time()))

        if coded_district_key not in td:
            td.append_data({
                coded_district_key: "none"
            }, Metadata(user, Metadata.get_call_location(), time.time()))

        is_mogadishu = td[coded_district_key] in mogadishu_districts
        td.append_data({
            "Raw FGD/CC Response": td["Response_1 (Text) - wt_fgd_cc"],
            "FGD/CC Consented": td[fgd_cc_consent_key],
            "Raw District": td[raw_district_key],
            "Coded District":
                td[coded_district_key] if td[raw_district_key] != Codes.TRUE_MISSING else Codes.TRUE_MISSING,
            "Coded Age": td[coded_age_key] if td[raw_age_key] != Codes.TRUE_MISSING else Codes.TRUE_MISSING,
            "Coded Gender": td[coded_gender_key] if td[raw_gender_key] != Codes.TRUE_MISSING else Codes.TRUE_MISSING,
            "District Mogadishu": Codes.YES if is_mogadishu else Codes.NO,
            "FGD/CC Consented and District Mogadishu":
                Codes.YES if is_mogadishu and td[fgd_cc_consent_key] == Codes.YES else Codes.NO
        }, Metadata(user, Metadata.get_call_location(), time.time()))

    # Filter out respondents who aren't from Mogadishu
    fgd_cc_data = [td for td in fgd_cc_data if td["District Mogadishu"] == Codes.YES]

    # Filter out respondents who are definitely younger than 18
    adults = []
    for td in fgd_cc_data:
        try:
            age = int(td["Coded Age"])
            if age >= MINIMUM_AGE:
                adults.append(td)
        except:
            adults.append(td)
    fgd_cc_data = adults

    # Rename columns for final output
    for td in fgd_cc_data:
        td.append_data({
            "Phone Number": "+{}".format(phone_uuids.get_phone(td["avf_phone_id"])),
            "Gender": td["Coded Gender"],
            "Age": td["Coded Age"],
            "District": "mogadishu" if td["Coded District"] == "mogadisho" else td["Coded District"]
        }, Metadata(user, Metadata.get_call_location(), time.time()))

    # Shuffle output
    random.seed(0)
    random.shuffle(fgd_cc_data)

    # Write json output
    IOUtils.ensure_dirs_exist_for_file(json_output_path)
    with open(json_output_path, "w") as f:
        TracedDataJsonIO.export_traced_data_iterable_to_json(fgd_cc_data, f, pretty_print=True)

    # Set call center data
    cc_data = fgd_cc_data[:TOTAL_CC_CONTACTS]
    fgd_cc_data = fgd_cc_data[TOTAL_CC_CONTACTS:]

    # Set focus group discussion data
    fgd_data = []
    male_count = 0
    female_count = 0
    target_count = TOTAL_FGD_CONTACTS
    for td in fgd_cc_data:
        if td["Gender"] == Codes.MALE and male_count < target_count / 2:
            male_count += 1
            fgd_data.append(td)
        if td["Gender"] == Codes.FEMALE and female_count < target_count / 2:
            female_count += 1
            fgd_data.append(td)

    # Output to focus group discussion/call center CSVs
    headers = [
        "Phone Number",
        "Gender",
        "Age",
        "District"
    ]
    with open(fgd_csv_output_path, "w") as f:
        TracedDataCSVIO.export_traced_data_iterable_to_csv(fgd_data, f, headers)

    with open(cc_csv_output_path, "w") as f:
        TracedDataCSVIO.export_traced_data_iterable_to_csv(cc_data, f, headers)
