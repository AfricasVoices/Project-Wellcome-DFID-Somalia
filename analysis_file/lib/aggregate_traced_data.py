import time

from core_data_modules.cleaners import Codes
from core_data_modules.traced_data import Metadata
from dateutil.parser import isoparse


class AggregateTracedData(object):
    @staticmethod
    def aggregate_messages(user, td_1, td_2):
        agg_d = dict()

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
            agg_d[key] = td_1[key]

        agg_d["date_time"] = td_1["date_time"]
        for k in ["raw_radio_q1", "raw_radio_q2", "raw_radio_q3", "raw_radio_q4"]:
            if td_1.get(k, Codes.TRUE_MISSING) != Codes.TRUE_MISSING and td_2.get(k, Codes.TRUE_MISSING) != Codes.TRUE_MISSING:
                agg_d["date_time"] = td_1["date_time"][0:10]
                agg_d[k] = "{};{}".format(td_1[k], td_2[k])

        for k in ["radio_q1", "radio_q2"]:
            if td_1.get(k) == "stop" or td_2.get(k) == "stop":
                agg_d[k] = "stop"
            elif td_1.get(k) == td_2.get(k):
                agg_d[k] = td_1.get(k)
            elif (td_1.get(k) == Codes.YES and td_2.get(k) == Codes.NO) or \
                    (td_1.get(k) == Codes.NO and td_2.get(k) == Codes.YES):
                agg_d[k] = "both"
            elif td_1.get(k) is None:
                agg_d[k] = td_2.get(k)
            else:
                agg_d[k] = td_1.get(k)

        if td_1["message_type"] != td_2["message_type"]:
            agg_d["message_type"] = "NC"

        if td_1["radio_show"] != td_2["radio_show"]:
            agg_d["radio_show"] = "NC"

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

        for key in td_1:
            if key.startswith("radio_q1_") or key.startswith("radio_q2_") or key.startswith("radio_q3_") or \
                    key.startswith("radio_q4_") or \
                    key.startswith("trustworthy_advisors_clean_") or key.startswith("outbreak_action_"):
                if td_1[key] == Codes.TRUE_MISSING:
                    agg_d[key] = Codes.TRUE_MISSING
                else:
                    agg_d[key] = "1" if td_1[key] == "1" or td_2[key] == "1" else "0"
                same_keys.append(key)
            if key not in same_keys:
                agg_d[key] = "PRE_MERGE_UNIFICATION"

        td_out = td_1.copy()
        td_out.append_data(agg_d, Metadata(user, Metadata.get_call_location(), time.time()))
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
