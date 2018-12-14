import argparse
import os
import time
from os import path
import hashlib
from dateutil.parser import isoparse
import jsonpickle
import datetime
import json
import csv

from core_data_modules.cleaners import swahili, Codes
from core_data_modules.traced_data import Metadata, TracedData
from core_data_modules.traced_data.io import TracedDataJsonIO, TracedDataCSVIO
from core_data_modules.util import IOUtils, PhoneNumberUuidTable, sha_utils


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cleans the surveys and exports variables to Coda for "
                                                 "manual verification and coding")
    parser.add_argument("input_path", metavar="input_path",
                        help="Path to csv input file containing the call centre data")
    parser.add_argument("coda_output_path", metavar="coda-output-path",
                        help="Directory to write coda files to")

    args = parser.parse_args()
    input_path = args.input_path
    coda_output_path = args.coda_output_path

    print ("Reading csv file")
    f = open(input_path, 'r')
    reader = csv.reader(f)
    headers = next(reader, None)

    headers_to_datasets = {
        "informationcc_raw_radio_q1_why" : ["Wellcome_cc_RQ1"],
        "informationcc_raw_radio_q2_why" : ["Wellcome_cc_RQ2"],
        "informationcc_raw_radio_q3" : ["Wellcome_cc_RQ3"],
        "informationcc_raw_radio_q4" : ["Wellcome_cc_RQ4"],
        "informationcc_raw_radio_q5_why" : ["Wellcome_cc_RQ5"],
        "informationcc_trustworthy_adviso" : ["Wellcome_cc_trustworthy_advisors", "Wellcome_cc_outbreak_response"],
    }

    datasets = {}

    print (headers)
    IOUtils.ensure_dirs_exist(coda_output_path)

    for row in reader:
        for header in headers_to_datasets.keys():
            index = headers.index(header)
            for output_dataset in headers_to_datasets[header]:
                if output_dataset not in datasets:
                    datasets[output_dataset] = []

                datasets[output_dataset].append(row[index])

    for dataset_name in datasets.keys():
        seen_messages = set()
        messages = []
        for text in datasets[dataset_name]:
            if text in seen_messages:
                continue
            
            seen_messages.add(text)
            messages.append({
                "Labels" : {},
                "MessageID" : sha_utils.SHAUtils.sha_string(text),
                "Text" : text,
                "CreationDateTimeUTC" : datetime.datetime.now().isoformat()
            })

        output_path = os.path.join(coda_output_path, dataset_name + ".json")
        f = open (output_path, 'w')
        json.dump(messages, f, indent=2)
