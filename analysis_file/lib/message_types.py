from core_data_modules.cleaners import Codes
from dateutil.parser import isoparse


class MessageTypes(object):
    promo_dates = [
        ["2018-07-22T06:25:00+03:00", "2018-07-23T00:00:00+03:00"],
        ["2018-07-23T00:00:00+03:00", "2018-07-24T00:00:00+03:00"],
        ["2018-07-24T00:00:00+03:00", "2018-07-25T00:00:00+03:00"],
        ["2018-07-25T00:00:00+03:00", "2018-07-26T00:00:00+03:00"],
        ["2018-07-26T00:00:00+03:00", "2018-07-26T19:00:00+03:00"],

        ["2018-07-29T06:25:00+03:00", "2018-07-30T00:00:00+03:00"],
        ["2018-07-30T00:00:00+03:00", "2018-07-31T00:00:00+03:00"],
        ["2018-07-31T00:00:00+03:00", "2018-08-01T00:00:00+03:00"],
        ["2018-08-01T00:00:00+03:00", "2018-08-02T00:00:00+03:00"],
        ["2018-08-02T00:00:00+03:00", "2018-08-02T19:00:00+03:00"],

        ["2018-08-05T06:25:00+03:00", "2018-08-06T00:00:00+03:00"],
        ["2018-08-06T00:00:00+03:00", "2018-08-07T00:00:00+03:00"],
        ["2018-08-07T00:00:00+03:00", "2018-08-08T00:00:00+03:00"],
        ["2018-08-08T00:00:00+03:00", "2018-08-09T00:00:00+03:00"],
        ["2018-08-09T00:00:00+03:00", "2018-08-09T19:00:00+03:00"],

        ["2018-08-12T06:25:00+03:00", "2018-08-13T00:00:00+03:00"],
        ["2018-08-13T00:00:00+03:00", "2018-08-14T00:00:00+03:00"],
        ["2018-08-14T00:00:00+03:00", "2018-08-15T00:00:00+03:00"],
        ["2018-08-15T00:00:00+03:00", "2018-08-16T00:00:00+03:00"],
        ["2018-08-16T00:00:00+03:00", "2018-08-16T19:00:00+03:00"],

        ["2018-08-19T06:25:00+03:00", "2018-08-20T00:00:00+03:00"],
        ["2018-08-20T00:00:00+03:00", "2018-08-21T00:00:00+03:00"],
        ["2018-08-21T00:00:00+03:00", "2018-08-22T00:00:00+03:00"],
        ["2018-08-22T00:00:00+03:00", "2018-08-23T00:00:00+03:00"],
        ["2018-08-23T00:00:00+03:00", "2018-08-23T19:00:00+03:00"]
    ]

    advert_dates = [
        ["2018-07-26T19:00:00+03:00", "2018-07-27T00:00:00+03:00"],
        ["2018-07-27T00:00:00+03:00", "2018-07-27T08:30:00+03:00"],

        ["2018-08-02T19:00:00+03:00", "2018-08-03T00:00:00+03:00"],
        ["2018-08-03T00:00:00+03:00", "2018-08-03T08:30:00+03:00"],

        ["2018-08-09T19:00:00+03:00", "2018-08-10T00:00:00+03:00"],
        ["2018-08-10T00:00:00+03:00", "2018-08-10T08:30:00+03:00"],

        ["2018-08-16T19:00:00+03:00", "2018-08-17T00:00:00+03:00"],
        ["2018-08-17T00:00:00+03:00", "2018-08-17T08:30:00+03:00"],

        ["2018-08-23T19:00:00+03:00", "2018-08-24T00:00:00+03:00"],
        ["2018-08-24T00:00:00+03:00", "2018-08-24T08:30:00+03:00"],
    ]

    show_dates = [
        ["2018-07-27T08:30:00+03:00", "2018-07-28T00:00:00+03:00"],
        ["2018-07-28T00:00:00+03:00", "2018-07-29T00:00:00+03:00"],
        ["2018-07-29T00:00:00+03:00", "2018-07-29T06:25:00+03:00"],

        ["2018-08-03T08:30:00+03:00", "2018-08-04T00:00:00+03:00"],
        ["2018-08-04T00:00:00+03:00", "2018-08-05T00:00:00+03:00"],
        ["2018-08-05T00:00:00+03:00", "2018-08-05T06:25:00+03:00"],

        ["2018-08-10T08:30:00+03:00", "2018-08-11T00:00:00+03:00"],
        ["2018-08-11T00:00:00+03:00", "2018-08-12T00:00:00+03:00"],
        ["2018-08-12T00:00:00+03:00", "2018-08-12T06:25:00+03:00"],

        ["2018-08-17T08:30:00+03:00", "2018-08-18T00:00:00+03:00"],
        ["2018-08-18T00:00:00+03:00", "2018-08-19T00:00:00+03:00"],
        ["2018-08-19T00:00:00+03:00", "2018-08-19T06:25:00+03:00"],

        ["2018-08-24T08:30:00+03:00", "2018-08-25T00:00:00+03:00"],
        ["2018-08-25T00:00:00+03:00", "2018-08-26T00:00:00+03:00"],
        ["2018-08-26T00:00:00+03:00", "2018-08-26T06:25:00+03:00"]
    ]

    @classmethod
    def for_date_string(cls, iso_date):
        """
        Computes the message type for a message sent at the time given by the provided iso_date string.

        :param iso_date: Date to determine message type of.
        :type iso_date: string in ISO8601 format.
        :return: "promo" | "advert" | "show"
        :rtype: str
        """
        dt = isoparse(iso_date)

        total_matches = 0
        message_type = ""
        for promo_range in cls.promo_dates:
            if isoparse(promo_range[0]) <= dt < isoparse(promo_range[1]):
                message_type = "promo"
                total_matches += 1

        for advert_range in cls.advert_dates:
            if isoparse(advert_range[0]) <= dt < isoparse(advert_range[1]):
                message_type = "advert"
                total_matches += 1

        for show_range in cls.show_dates:
            if isoparse(show_range[0]) <= dt < isoparse(show_range[1]):
                message_type = "show"
                total_matches += 1

        if total_matches == 0:
            print("Warning: '{}' has no matching promo, advert, or show".format(iso_date))
            return "NC"  # TODO: Change to "Codes.NOT_CODED"
        if total_matches > 1:
            print("Warning: '{}' matches multiple promos, adverts, and/or shows".format(iso_date))
            return "NC"  # TODO: Change to "Codes.NOT_CODED"

        return message_type

    @classmethod
    def for_show(cls, show_number, td):
        """
        Computes the message type for a message sent for show 'show_number' in the given TracedData object.

        :param show_number: Number of show to export, in range 1-5 inclusive
        :type show_number: int
        :param td: TracedData item to get message_type of.
        :type td: TracedData
        :return: "promo" | "advert" | "show"
        :rtype: str
        """
        if show_number == 1:
            return cls.for_date_string(td["S06E01_Risk_Perception (Time) - wt_s06e1_activation"])
        elif show_number == 2:
            return cls.for_date_string(td["S06E02_Cholera_Preparedness (Time) - wt_s06e2_activation"])
        elif show_number == 3:
            return cls.for_date_string(td["S06E03_Outbreak_Knowledge (Time) - wt_s06e03_activation"])
        elif show_number == 4:
            return cls.for_date_string(td["S06E04_Cholera_Recurrency (Time) - wt_s06e04_activation"])
        elif show_number == 5:
            return cls.for_date_string(td["S06E05_Water_Quality (Time) - wt_s06e05_activation"])
        else:
            assert False, "Unknown show number '{}'. Must be in range 1-5 inclusive".format(show_number)
