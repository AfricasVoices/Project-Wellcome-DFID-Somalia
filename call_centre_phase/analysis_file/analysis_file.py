import sys
import time
import argparse
import os
import json
import sys

from core_data_modules.cleaners import Codes
from core_data_modules.traced_data import Metadata
from core_data_modules.traced_data.io import TracedDataCSVIO, TracedDataJsonIO
from core_data_modules.traced_data.util import FoldTracedData

from lib.analysis_keys import AnalysisKeys
from lib.code_books import CodeBooks

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("user")
    parser.add_argument("coding_schemes_path", metavar="coding-schemes-path", help="Directory containing coding schemes")
    parser.add_argument("data_path")
    parser.add_argument("csv_by_message_output_path")
    parser.add_argument("csv_by_individual_output_path")

    args = parser.parse_args()
    user = args.user
    coding_schemes_path = args.coding_schemes_path
    data_path = args.data_path
    csv_by_message_output_path = args.csv_by_message_output_path
    csv_by_individual_output_path = args.csv_by_individual_output_path

    with open(data_path) as f:
        data = TracedDataJsonIO.import_json_to_traced_data_iterable(f)

    coding_schemes = {}

    for filename in os.listdir(coding_schemes_path):
        with open(os.path.join(coding_schemes_path, filename)) as f:
            # TODO: Switch to use Scheme.from_firebase_map()
            coding_schemes[filename.split(".json")[0]] = json.load(f)
    
    code_ids = dict()
    for scheme in coding_schemes:
        scheme_dict = coding_schemes[scheme]
        codes = scheme_dict["Codes"]
        code_ids[scheme_dict["Name"]] = {}
        for code in codes:
            if "ControlCode" in code:
                code_text = code["ControlCode"]
            else:
                code_text = code["DisplayText"]
            code_ids[scheme_dict["Name"]][code["CodeID"]] = code_text

    class CodingPlan(object):
        def __init__(self, raw_field, coded_field, coda_filename=None, cleaner=None, code_scheme=None, time_field=None,
                    run_id_field=None, icr_filename=None, analysis_file_key=None):
            self.raw_field = raw_field
            self.coded_field = coded_field
            self.coda_filename = coda_filename
            self.icr_filename = icr_filename
            self.cleaner = cleaner
            if code_scheme is None:
                self.code_scheme = list()
            else:
                self.code_scheme = code_scheme
            self.time_field = time_field
            self.run_id_field = run_id_field
            self.analysis_file_key = analysis_file_key


    INDIVIDUAL_CODING_PLANS = [
    CodingPlan(raw_field="informationcc_raw_radio_q3",
                coded_field="informationcc_raw_radio_q3_Coded",
                analysis_file_key="cc_radio_q3_exp",
                code_scheme=coding_schemes["Wellcome_cc_RQ3_Frame"]),

    CodingPlan(raw_field="informationcc_raw_radio_q4",
                coded_field="informationcc_raw_radio_q4_Coded",
                analysis_file_key="cc_radio_q4_exp",
                code_scheme=coding_schemes["Wellcome_cc_RQ4_Frame"]),

    CodingPlan(raw_field="informationcc_raw_radio_q5_why",
                coded_field="informationcc_raw_radio_q5_why_Coded",
                analysis_file_key="cc_radio_q5_exp",
                code_scheme=coding_schemes["Wellcome_cc_RQ5_Frame"])
    ]

    MATRIX_CODING_PLANS = [
    CodingPlan(raw_field="informationcc_raw_radio_q1_why",
                coded_field="informationcc_raw_radio_q1_why_Coded",
                analysis_file_key="cc_radio_q1_[yes|no]_exp_",
                code_scheme=[coding_schemes["Wellcome_cc_RQ1_Frame"]]),
    
    CodingPlan(raw_field="informationcc_raw_radio_q2_why",
                coded_field="informationcc_raw_radio_q2_why_Coded",
                analysis_file_key="cc_radio_q2_[yes|no]_exp_",
                code_scheme=[coding_schemes["Wellcome_cc_RQ2_Frame"]]),
    
    CodingPlan(raw_field="informationcc_raw_radio_trustworthy_advisors",
                coded_field="informationcc_raw_radio_trustworthy_adviso_Coded",
                analysis_file_key="cc_radio_trustworthy_advisors_exp_",
                code_scheme=[coding_schemes["Trustworthy_advisors"], coding_schemes["Outbreak_response"]])
    ]

    REMAP_PLANS = [
    CodingPlan(raw_field="date",
                coded_field=None,
                analysis_file_key="cc_date",
                code_scheme=None),
                
    CodingPlan(raw_field="uuid",
                coded_field=None,
                analysis_file_key="cc_id",
                code_scheme=None),
                            
    CodingPlan(raw_field="introcc_consent",
                coded_field=None,
                analysis_file_key="cc_consent",
                code_scheme=None),

    CodingPlan(raw_field="cc_district",
                coded_field=None,
                analysis_file_key="cc_district_mog",
                code_scheme=None),

    CodingPlan(raw_field="informationcc_urban_rural",
                coded_field=None,
                analysis_file_key="cc_urban_rural ",
                code_scheme=None),

    CodingPlan(raw_field="ben_gender",
                coded_field=None,
                analysis_file_key="cc_gender",
                code_scheme=None),

    CodingPlan(raw_field="informationcc_radio_station1",
                coded_field=None,
                analysis_file_key="cc_radio_station",
                code_scheme=None),

    CodingPlan(raw_field="informationcc_radio_station2",
                coded_field=None,
                analysis_file_key="cc_radio_station",
                code_scheme=None),

    CodingPlan(raw_field="informationcc_radio_station3",
                coded_field=None,
                analysis_file_key="cc_radio_station",
                code_scheme=None),

    CodingPlan(raw_field="informationcc_radio_station4",
                coded_field=None,
                analysis_file_key="cc_radio_station",
                code_scheme=None),

    CodingPlan(raw_field="informationcc_radio_station5",
                coded_field=None,
                analysis_file_key="cc_radio_station",
                code_scheme=None),

    CodingPlan(raw_field="informationcc_kalkaal",
                coded_field=None,
                analysis_file_key="cc_kalkaal",
                code_scheme=None),

    CodingPlan(raw_field="ben_age",
                coded_field=None,
                analysis_file_key="cc_age",
                code_scheme=None),

    CodingPlan(raw_field="informationcc_education",
                coded_field=None,
                analysis_file_key="cc_education",
                code_scheme=None),

    CodingPlan(raw_field="informationcc_idp",
                coded_field=None,
                analysis_file_key="cc_idp",
                code_scheme=None),

    CodingPlan(raw_field="informationcc_origin_district",
                coded_field=None,
                analysis_file_key="cc_origin_district",
                code_scheme=None),

    CodingPlan(raw_field="informationcc_household_sickness",
                coded_field=None,
                analysis_file_key="cc_household_sickness",
                code_scheme=None),
                
    CodingPlan(raw_field="informationcc_sickness_txt",
                coded_field=None,
                analysis_file_key="cc_household_sickness_expl",
                code_scheme=None),

    CodingPlan(raw_field="informationcc_cholera_vaccinatio",
                coded_field=None,
                analysis_file_key="cc_cholera_vaccination",
                code_scheme=None),

    CodingPlan(raw_field="informationcc_raw_radio_q1",
                coded_field=None,
                analysis_file_key="cc_raw_radio_q1",
                code_scheme=None),
                
    CodingPlan(raw_field="informationcc_raw_radio_q2",
                coded_field=None,
                analysis_file_key="cc_raw_radio_q2",
                code_scheme=None),

    CodingPlan(raw_field="informationcc_raw_radio_q3",
                coded_field=None,
                analysis_file_key="cc_raw_radio_q3",
                code_scheme=None),

    CodingPlan(raw_field="informationcc_raw_radio_q4",
                coded_field=None,
                analysis_file_key="cc_raw_radio_q4",
                code_scheme=None),

    CodingPlan(raw_field="informationcc_raw_radio_q5",
                coded_field=None,
                analysis_file_key="cc_raw_radio_q5",
                code_scheme=None),

    CodingPlan(raw_field="informationcc_raw_radio_q1_why",
                coded_field=None,
                analysis_file_key="cc_radio_q1_[yes|no]_exp",
                code_scheme=None),

    ]
    
    # Serializer is currently overflowing
    # TODO: Investigate/address the cause of this.
    sys.setrecursionlimit(10000)

    # Set the list of raw/coded keys
    individual_keys = []
    for plan in INDIVIDUAL_CODING_PLANS:
        if plan.analysis_file_key not in individual_keys:
            individual_keys.append(plan.analysis_file_key)
        if plan.raw_field not in individual_keys:
            individual_keys.append(plan.raw_field)

    individual_keys.sort()

    print("Creating individual analysis keys/coded values")
    for td in data:
        for plan in INDIVIDUAL_CODING_PLANS:
            if plan.coded_field in td:
                td.append_data(
                    {plan.analysis_file_key: code_ids[plan.code_scheme["Name"]][td[plan.coded_field]["CodeID"]]},
                    Metadata(user, Metadata.get_call_location(), time.time())
                    )
                    
            else:
                td.append_data({plan.analysis_file_key: Codes.TRUE_MISSING},
                    Metadata(user, Metadata.get_call_location(), time.time())
                    )
                td.append_data({plan.coded_field: Codes.TRUE_MISSING},
                    Metadata(user, Metadata.get_call_location(), time.time())
              )
    
    remapped_keys = []
    for plan in REMAP_PLANS:
        if plan.analysis_file_key not in remapped_keys:
            remapped_keys.append(plan.analysis_file_key)
        if plan.raw_field not in remapped_keys:
            remapped_keys.append(plan.raw_field)

    for td in data:
        for plan in REMAP_PLANS:
            td.append_data(
                {plan.analysis_file_key: plan.raw_field},
                Metadata(user, Metadata.get_call_location(), time.time())
            )

    # Translate keys to final values for analysis
    matrix_keys = []

    print("Creating matrix analysis keys/coded values")
    for plan in MATRIX_CODING_PLANS:
        for code_scheme in plan.code_scheme:
            show_matrix_keys = set()
            for code_scheme in plan.code_scheme:
                for code in code_ids[code_scheme["Name"]]:
                    show_matrix_keys.add(f"{plan.analysis_file_key}{code_ids[code_scheme['Name']][code]}")

            AnalysisKeys.set_matrix_keys(
                user, data, show_matrix_keys, code_scheme["Name"], code_ids, plan.coded_field, plan.analysis_file_key)

            matrix_keys.extend(show_matrix_keys)

    matrix_keys.sort()

    equal_keys = ["avf_phone_id"]
    equal_keys.extend(individual_keys)

    print("Folding")
    folded = FoldTracedData.fold_iterable_of_traced_data(
    user, data, lambda td: (td["avf_phone_id"]), equal_keys=equal_keys, matrix_keys=matrix_keys
    )

    print("Post fold fix-up")

    # Apply codebooks

    codebooks = {
        "cc_part_type": CodeBooks.cc_part_type,
        "cc_consent": CodeBooks.yes_no,
        "cc_district_mog": CodeBooks.cc_district,
        "cc_urban_rural": CodeBooks.informationcc_urban_rural,
        "cc_gender": CodeBooks.ben_gender,

    }

    # Export to CSV
    export_keys = ["avf_phone_id"]
    export_keys.extend(individual_keys)
    export_keys.extend(matrix_keys)
    export_keys.sort()

    print("Writing 1/2")
    with open(csv_by_individual_output_path, "w") as f:
        TracedDataCSVIO.export_traced_data_iterable_to_csv(folded, f, headers=export_keys)

    """
    print("Writing 2/2")
    with open(csv_by_message_output_path, "w") as f:
        #TracedDataJsonIO.export_traced_data_iterable_to_json(data, f, pretty_print=True)
        TracedDataCSVIO.export_traced_data_iterable_to_csv(data, f, headers=export_keys)
    """