import argparse
import unicodecsv
import os
import time
import uuid

from core_data_modules.traced_data import TracedData, Metadata
from core_data_modules.traced_data.io import TracedDataJsonIO
from core_data_modules.util import PhoneNumberUuidTable

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Imports call center dataset csv to TracedData and assigns UUIDs")
    parser.add_argument("user", help="Identifier of user launching this program, for use in TracedData Metadata")
    parser.add_argument("call_center_input_csv_path", metavar="call-center-input-csv-path")
    parser.add_argument("json_output_path", metavar="json-output-path")

    args = parser.parse_args()
    user = args.user
    call_center_input_csv_path = args.call_center_input_csv_path
    json_output_path = args.json_output_path

    with open(call_center_input_csv_path, "rb") as f:
        reader = unicodecsv.DictReader(f)
        header = ["avf_phone_id"] + reader.fieldnames
        reader = list(reader)
        for row in reader:
            row["avf_phone_id"] = uuid.uuid4().hex
    
    traced_date_iterable = list()
    for row in reader:
        traced_date_iterable.append(TracedData(dict(row), Metadata(user, Metadata.get_call_location(), time.time())))

    with open(json_output_path, "w") as f:
        TracedDataJsonIO.export_traced_data_iterable_to_json(traced_date_iterable, f, pretty_print=True)

    