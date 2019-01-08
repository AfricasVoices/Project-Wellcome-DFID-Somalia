import time

from core_data_modules.cleaners import Codes
from core_data_modules.traced_data import Metadata

class CodeBooks(object):
    cc_part_type = {
        "host": 1,
        "idp": 2,
        "kalkaal": 3
    }

    cc_district = {
        "Wadajir medina": 1,
        "Heliwa": 2,
        "Xamar jabjjab": 3,
        "Shangaani": 4,
        "Waaberi": 5,
        "Hawl wadaag": 6,
        "Xamar weyne": 7,
        "Shibis": 8,
        "Dharkeynley": 9,
        "Abdulaziz": 10,
        "Boondheere": 11,
        "Wadajir": 12,
        "Kaxda": 13,
        "Daynille": 14,
        "Yaaqshiid": 15,
        "Hodan": 16,
        "Kaaraan": 17
    }

    informationcc_urban_rural = {
        "rural": 1,
        "urban": 2
    }

    ben_gender = {
        "male": 1,
        "female": 2
    }

    informationcc_radio_station1 = {
        "TRUE":1
    }
    informationcc_radio_station2 = {
        "TRUE":2
    }
    informationcc_radio_station3 = {
        "TRUE":3
    }
    informationcc_radio_station4 = {
        "TRUE":4
    }
    informationcc_radio_station5 = {
        "TRUE":5
    }

    informationcc_education = {
        "no_school": 1,
        "primary": 2,
        "secondary": 3,
        "colle_uni": 4,
        "islamic": 5
    }

    yes_no = {
        "1": 2,
        "2": 1
    }

    missing = {
        Codes.SKIPPED: 777,
        "NC": 888,
        "belong to other": 888,
        Codes.TRUE_MISSING: 999,
        None: None,
        "stop": "stop"  # TODO: Codes.STOP in Core Data
    }


    @classmethod
    def apply(cls, user, code_books, td):
        code_book_data = dict()
        for coded_key, code_book in code_books.items():
            code_book_data[coded_key] = cls.apply_code_book(code_book, td[coded_key])
        td.append_data(code_book_data, Metadata(user, Metadata.get_call_location(), time.time()))

    @classmethod
    def apply_code_book(cls, code_book, coded_response):
        if coded_response in code_book:
            return code_book[coded_response]
        elif coded_response in cls.missing:
            return cls.missing[coded_response]
        else:
            pass
            # assert False, # TODO: assert message
            pass

    @classmethod
    def apply_missing_code_book(cls, coded_response):
        return cls.missing.get(coded_response, coded_response)

