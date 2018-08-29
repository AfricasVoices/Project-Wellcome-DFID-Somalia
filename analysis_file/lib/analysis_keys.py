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
        Returns the coded value for a response if one was provided, otherwise returns Codes.TRUE_MISSING

        :param td: TracedData item to return the coded value of
        :type td: TracedData
        :param key_of_raw: Key in td of the raw response
        :type key_of_raw: str
        :param key_of_coded: Key in td of the coded response. Defaults to '<key_of_raw>_coded' if None
        :type key_of_coded: str
        :return: The coded value for a response if one was provided, otherwise Codes.TRUE_MISSING
        :rtype: str
        """
        if key_of_coded is None:
            key_of_coded = "{}_coded".format(key_of_raw)

        if td[key_of_raw] == Codes.TRUE_MISSING:
            return Codes.TRUE_MISSING
        else:
            return td[key_of_coded]

    @classmethod
    def get_origin_district(cls, td):
        """
        Returns Codes.SKIPPED if this respondent has answered "no" to the IDP question; otherwise returns their
        origin district as normal via cls.get_code

        :param td: TracedData item to get the origin district from
        :type td: TracedData
        :return: Coded origin district
        :rtype: str
        """
        if cls.get_code(td, "Idp (Text) - wt_demog_2") == Codes.NO:
            return Codes.SKIPPED
        else:
            return cls.get_code(td, "Origin_District (Text) - wt_demog_2")

    @staticmethod
    def get_date_time_utc(td):
        return isoparse(td["created_on"]).strftime("%Y-%m-%d %H:%M")

    @staticmethod
    def get_date_time_eat(td):
        return isoparse(td["created_on"]).astimezone(pytz.timezone("Africa/Nairobi")).strftime("%Y-%m-%d %H:%M")

    @classmethod
    def set_analysis_keys(cls, user, show_number, td):
        td.append_data({
            "date_time_utc": cls.get_date_time_utc(td),
            "date_time": cls.get_date_time_eat(td),
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
