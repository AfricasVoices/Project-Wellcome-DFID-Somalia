import time

import pytz
from core_data_modules.cleaners import Codes
from core_data_modules.traced_data import Metadata
from dateutil.parser import isoparse

from lib.message_types import MessageTypes


class AnalysisKeys(object):
    @staticmethod
    def get_code(td, key_of_raw, key_of_coded=None):
        """
        Returns Codes.TRUE_MISSING if a given TracedData item does not contain

        :param td:
        :type td:
        :param key_of_raw:
        :type key_of_raw:
        :param key_of_coded:
        :type key_of_coded:
        :return:
        :rtype:
        """
        if key_of_coded is None:
            key_of_coded = "{}_coded".format(key_of_raw)

        if td[key_of_raw] == Codes.TRUE_MISSING:
            return Codes.TRUE_MISSING
        else:
            return td[key_of_coded]

    @classmethod
    def get_origin_district(cls, td):
        if cls.get_code(td, "Idp (Text) - wt_demog_2") == Codes.NO:  # TODO: Change to Codes.NO once recoded.
            return Codes.SKIPPED
        else:
            return cls.get_code(td, "Origin_District (Text) - wt_demog_2")

    @classmethod
    def set_analysis_keys(cls, user, show_number, td):
        td.append_data({
            "date_time_utc": isoparse(td["created_on"]).strftime("%Y-%m-%d %H:%M"),
            "date_time":
                isoparse(td["created_on"]).astimezone(pytz.timezone("Africa/Nairobi")).strftime("%Y-%m-%d %H:%M"),
            "phone_uuid": td["avf_phone_id"],

            "district_clean": cls.get_code(td, "District (Text) - wt_demog_1"),
            "urban_rural_clean": cls.get_code(td, "Urban_Rural (Text) - wt_demog_1"),
            "gender_clean": cls.get_code(td, "Gender (Text) - wt_demog_1"),

            "radio_station_clean": cls.get_code(td, "Radio_Station (Text) - wt_demog_2"),
            "age_clean": cls.get_code(td, "Age (Text) - wt_demog_2"),
            "education_clean": cls.get_code(td, "Education_Level (Text) - wt_demog_2"),
            "idp_clean": cls.get_code(td, "Idp (Text) - wt_demog_2"),
            "origin_district_clean": cls.get_origin_district(td),

            "household_sickness_clean": cls.get_code(td, "Household_Sickness (Text) - wt_practice"),
            "sickness_adult_child": cls.get_code(td, "Household_Sickness (Text) - wt_practice",
                                                 "Household_Sickness (Text) - wt_practice_coded_people"),
            "cholera_vaccination_clean": cls.get_code(td, "Cholera_Vaccination (Text) - wt_practice"),
            "trustworthy_advisors_clean": cls.get_code(td, "Trustworthy_Advisors (Text) - wt_practice"),

            "radio_show": show_number,
            "message_type": MessageTypes.for_show(show_number, td),

            "raw_radio_q1": td.get("S06E01_Risk_Perception (Text) - wt_s06e1_activation", "NS"),
            "raw_radio_q2": td.get("S06E02_Cholera_Preparedness (Text) - wt_s06e2_activation", "NS"),
            "raw_radio_q3": td.get("S06E03_Outbreak_Knowledge (Text) - wt_s06e03_activation", "NS"),
            "raw_radio_q4": td.get("S06E04_Cholera_Recurrency (Text) - wt_s06e04_activation", "NS"),
            "raw_radio_q5": td.get("S06E05_Water_Quality (Text) - wt_s06e05_activation", "NS")
        }, Metadata(user, Metadata.get_call_location(), time.time()))
