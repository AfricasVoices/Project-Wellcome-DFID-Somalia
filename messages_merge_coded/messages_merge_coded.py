import argparse

from core_data_modules.traced_data.io import TracedDataJsonIO, TracedDataCodaIO
from core_data_modules.util import IOUtils

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merges manually cleaned files back into a traced data file.")
    parser.add_argument("user", help="User launching this program, for use by TracedData Metadata")
    parser.add_argument("json_input_path", metavar="json-input-path",
                        help="Path to JSON input file, which contains a list of TracedData objects to code")
    parser.add_argument("coded_input_path", metavar="coded-input-path",
                        help="Coda file to import coded labels from")
    parser.add_argument("show_number", metavar="show-number",
                        help="")  # TODO
    parser.add_argument("json_output_path", metavar="json-output-path",
                        help="Path to a JSON file to write merged results to")

    args = parser.parse_args()
    user = args.user
    json_input_path = args.json_input_path
    coded_input_path = args.coded_input_path
    show_number = int(args.show_number)
    json_output_path = args.json_output_path

    # Load data from JSON file
    with open(json_input_path, "r") as f:
        show_messages = TracedDataJsonIO.import_json_to_traced_data_iterable(f)

    if show_number == 1:
        key_of_raw = "S06E01_Risk_Perception (Text) - wt_s06e1_activation"
        key_of_coded_prefix = "{}_coded_".format(key_of_raw)
        coda_yes_no_scheme = "Yes/No"
        coda_reason_schemes = {"Reason", "Reason 2"}
    elif show_number == 2:
        key_of_raw = "S06E02_Cholera_Preparedness (Text) - wt_s06e2_activation"
        key_of_coded_prefix = "{}_coded_".format(key_of_raw)
        coda_yes_no_scheme = "yes/no"
        coda_reason_schemes = {"Reasons"}
    elif show_number == 3:
        key_of_raw = "S06E03_Outbreak_Knowledge (Text) - wt_s06e03_activation"
        key_of_coded_prefix = "{}_coded_".format(key_of_raw)
        coda_yes_no_scheme = None
        coda_reason_schemes = {"default"}
    # TODO: Configure for other shows
    else:
        assert False, "Unrecognised show '{}'. Show should be a number from 1-5 inclusive.".format(show_number)

    # Merge yes/no responses from the manually coded Coda files into the cleaned dataset
    if coda_yes_no_scheme is not None:
        with open(coded_input_path, "r") as f:
            TracedDataCodaIO.import_coda_to_traced_data_iterable(
                user, show_messages, key_of_raw, {coda_yes_no_scheme: "{}yes_no".format(key_of_coded_prefix)}, f,
                overwrite_existing_codes=True)

    # Merge matrix data from the manually coded Coda files into the cleaned dataset
    with open(coded_input_path, "r") as f:
        TracedDataCodaIO.import_coda_to_traced_data_iterable_as_matrix(
            user, show_messages, key_of_raw, coda_reason_schemes, f, key_of_coded_prefix=key_of_coded_prefix)
        
    # Write coded data back out to disk
    IOUtils.ensure_dirs_exist_for_file(json_output_path)
    with open(json_output_path, "w") as f:
        TracedDataJsonIO.export_traced_data_iterable_to_json(show_messages, f, pretty_print=True)
