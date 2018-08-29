import time

from core_data_modules.cleaners import Codes
from core_data_modules.traced_data import Metadata
from dateutil.parser import isoparse


class AggregateTracedData(object):
    @staticmethod
    def aggregate_messages(user, td_1, td_2):
        new_d = dict()

        same_keys = [
            "phone_uuid",

            "district_clean",
            "urban_rural_clean",
            "gender_clean",

            "radio_station_clean",
            "age_clean",
            "education_clean",
            "idp_clean",
            "origin_district_clean",

            "household_sickness_clean",
            "sickness_adult_child",
            "cholera_vaccination_clean",
            "trustworthy_advisors_clean"
        ]

        for key in same_keys:
            assert td_1[key] == td_2[key], "Key '{}' has conflicting values: '{}' vs '{}'".format(key, td_1[key],
                                                                                                  td_2[key])
            new_d[key] = td_1[key]

        same_keys.extend([
            "date_time",
            "raw_radio_q1",
            "raw_radio_q2",
            "raw_radio_q3",
            "raw_radio_q4",
            "raw_radio_q5",
            "message_type",
            "radio_show",

            "radio_q1",
            "radio_q2"
        ])

        new_d["date_time"] = td_1["date_time"]
        if td_1.get("raw_radio_q1", Codes.SKIPPED) != Codes.SKIPPED and td_2.get("raw_radio_q1",
                                                                                 Codes.SKIPPED) != Codes.SKIPPED:
            new_d["date_time"] = td_1["date_time"][0:10]
            new_d["raw_radio_q1"] = "{};{}".format(td_1["raw_radio_q1"], td_2["raw_radio_q1"])
        if td_1.get("raw_radio_q2", Codes.SKIPPED) != Codes.SKIPPED and td_2.get("raw_radio_q2",
                                                                                 Codes.SKIPPED) != Codes.SKIPPED:
            new_d["date_time"] = td_1["date_time"][0:10]
            new_d["raw_radio_q2"] = "{};{}".format(td_1["raw_radio_q2"], td_2["raw_radio_q2"])
        if td_1.get("raw_radio_q3", Codes.SKIPPED) != Codes.SKIPPED and td_2.get("raw_radio_q3",
                                                                                 Codes.SKIPPED) != Codes.SKIPPED:
            new_d["date_time"] = td_1["date_time"][0:10]
            new_d["raw_radio_q3"] = "{};{}".format(td_1["raw_radio_q3"], td_2["raw_radio_q3"])

        if td_1.get("radio_q1") == "stop" or td_2.get("radio_q1") == "stop":
            new_d["radio_q1"] = "stop"
        else:
            new_d["radio_q1"] = td_1.get("radio_q1") if td_1.get("radio_q1") == td_2.get("radio_q1") else "NL"

        if td_1.get("radio_q2") == "stop" or td_2.get("radio_q2") == "stop":
            new_d["radio_q2"] = "stop"
        else:
            new_d["radio_q2"] = td_1.get("radio_q2") if td_1.get("radio_q2") == td_2.get("radio_q2") else "NL"

        if td_1["message_type"] != td_2["message_type"]:
            new_d["message_type"] = "NC"

        if td_1["radio_show"] != td_2["radio_show"]:
            new_d["radio_show"] = "NC"

        for key in td_1:
            if key.startswith("radio_q1_") or key.startswith("radio_q2_") or key.startswith("radio_q3_"):
                if td_1[key] == Codes.SKIPPED:
                    new_d[key] = Codes.SKIPPED
                else:
                    new_d[key] = "1" if td_1[key] == "1" or td_2[key] == "1" else "0"
                same_keys.append(key)
            if key not in same_keys:
                new_d[key] = "PRE_MERGE_UNIFICATION"

        td_out = td_1.copy()
        td_out.append_data(new_d, Metadata(user, Metadata.get_call_location(), time.time()))
        return td_out

    @classmethod
    def aggregate_by_respondent_and_date(cls, user, all_messages):
        grouped_responses = dict()  # of [avf_phone_id, date] -> (list of TracedData)
        for td in all_messages:
            key = (td["phone_uuid"], isoparse(td["date_time"]).strftime("%Y-%m-%d"))
            if key not in grouped_responses:
                grouped_responses[key] = []
            grouped_responses[key].append(td)

        collated_messages = []
        for messages in grouped_responses.values():
            out = messages.pop(0)
            while len(messages) > 0:
                out = cls.aggregate_messages(user, out, messages.pop(0))
            collated_messages.append(out)

        return collated_messages
