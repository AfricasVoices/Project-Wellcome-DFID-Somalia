import argparse
import os
import time

from core_data_modules.traced_data import TracedData, Metadata
from core_data_modules.traced_data.io import TracedDataJsonIO
from core_data_modules.util import PhoneNumberUuidTable
from dateutil.parser import isoparse
from temba_client.v2 import TembaClient

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Downloads the week 4 messages fom Rapid Pro that were not captured " 
                                                 "by the wt_s06e04_activation flow, and adds them to an existing "
                                                 "list of messages that were exported by normal means.")
    parser.add_argument("--server", help="Address of RapidPro server. Defaults to http://localhost:8000.",
                        nargs="?", default="http://localhost:8000")
    parser.add_argument("token", help="RapidPro API Token")
    parser.add_argument("user", help="Identifier of user launching this program, for use in TracedData Metadata")
    parser.add_argument("phone_uuid_table_path", metavar="phone-uuid-table-path",
                        help="JSON file containing an existing phone number <-> UUID lookup table. "
                             "This file will be updated with the new phone numbers which are found by this process")
    parser.add_argument("json_path", metavar="json-path",
                        help="Path to serialized TracedData JSON file containing a list of week 4 runs to be "
                             "updated. The update")

    args = parser.parse_args()
    server = args.server
    token = args.token
    user = args.user
    phone_uuid_path = args.phone_uuid_table_path
    json_path = args.json_path

    rapid_pro = TembaClient(server, token)

    # Load the existing phone number <-> UUID table.
    if not os.path.exists(phone_uuid_path):
        raise FileNotFoundError("No such phone uuid table file '{}'. "
                                "To create a new, empty UUID table, "
                                "run $ echo \"{{}}\" > <target-json-file>".format(phone_uuid_path))
    with open(phone_uuid_path, "r") as f:
        phone_uuids = PhoneNumberUuidTable.load(f)

    # Load the existing messages for week 4
    with open(json_path, "r") as f:
        week_4_messages = TracedDataJsonIO.import_json_to_traced_data_iterable(f)

    # Fetch messages in the S06e04 resend group
    mislocated_messages = rapid_pro.get_messages(label="S06e04_resend").all(retry_on_rate_exceed=True)
    print("Number of mislocated messages found: {}".format(len(mislocated_messages)))

    # Sort by ascending order of modification date.
    mislocated_messages = list(mislocated_messages)
    mislocated_messages.reverse()

    # Convert the mislocated messages to de-identified TracedData
    traced_messages = []
    for message in mislocated_messages:
        traced_messages.append(
            TracedData(
                {
                    "avf_phone_id": phone_uuids.add_phone(message.urn),
                    "id": message.id,
                    "text": message.text,
                    "created_on": message.created_on.isoformat(),
                    "sent_on": message.sent_on.isoformat(),
                    "modified_on": message.modified_on.isoformat()
                },
                Metadata(user, Metadata.get_call_location(), time.time())
            )
        )

    # Make the traced messages look like week 4 runs
    def format_label(parameter):
        """
        Creates a week 4 key for the given parameter.

        >>> format_label("Text")
        'S06E04_Cholera_Recurrency (Text) - wt_s06e04_activation'
        """
        category_title = "S06E04_Cholera_Recurrency"
        flow_name = "wt_s06e04_activation"
        return "{} ({}) - {}".format(category_title, parameter, flow_name)

    for traced_message in traced_messages:
        traced_message.append_data(
            {
                format_label("Category"): "All Responses",
                format_label("Value"): traced_message["text"],
                format_label("Text"): traced_message["text"],
                format_label("Name"): "s06e04_cholera_recurrency",
                format_label("Time"): traced_message["sent_on"],
                format_label("Run ID"): traced_message["id"],
                
                "exited_on": None,
                "exit_type": "completed"
            },
            Metadata(user, Metadata.get_call_location(), time.time())
        )

    # Merge the traced runs with previous data, ignoring messages which have already been included.
    def week_4_messages_contains_message(traced_message):
        for message in week_4_messages:
            if format_label("Text") in message and \
                    message[format_label("Text")] == traced_message[format_label("Text")] and \
                    message["avf_phone_id"] == traced_message["avf_phone_id"]:
                return True
        return False

    added_messages_count = 0
    for traced_message in traced_messages:
        if not week_4_messages_contains_message(traced_message):
            week_4_messages.append(traced_message)
            added_messages_count += 1
    print("Added {} messages".format(added_messages_count))

    # Write the UUIDs out to a file
    with open(phone_uuid_path, "w") as f:
        phone_uuids.dump(f)

    # Output the modified week_4_messages TracedData to JSON.
    if os.path.dirname(json_path) is not "" and not os.path.exists(os.path.dirname(json_path)):
        os.makedirs(os.path.dirname(json_path))
    with open(json_path, "w") as f:
        TracedDataJsonIO.export_traced_data_iterable_to_json(week_4_messages, f, pretty_print=True)
