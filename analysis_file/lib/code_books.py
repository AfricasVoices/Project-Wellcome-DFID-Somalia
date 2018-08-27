import time

from core_data_modules.cleaners import Codes
from core_data_modules.traced_data import Metadata


class CodeBooks(object):
    district = {
        "mogadisho": 1,
        "mogadishu": 1,
        "kismayo": 2,
        "baidoa": 3,
        "belet weyne": 4,

        "adan yabaal": 5,
        "afmadow": 6,
        "baardheere": 7,
        "baki": 8,
        "balad": 9,
        "balcad": 10,
        "bandarbayla": 11,
        "baraawe": 12,
        "berbera": 13,
        "boondheere": 14,
        "borama": 15,
        "bossaso": 16,
        "bu": 17,
        "bulo burto": 18,
        "burco": 19,
        "burtinle": 20,
        "buuhoodle": 21,
        "buur hakaba": 22,
        "cabdlcasiis": 23,
        "cabudwaaq": 24,
        "cadaado": 25,
        "caluula": 26,
        "caynabo": 27,
        "ceel afweyn": 28,
        "ceel buur": 29,
        "ceel waaq": 30,
        "ceerigaabo": 31,
        "daynile": 32,
        "dharkenley": 33,
        "dhuusamarreeb": 34,
        "doolow": 35,
        "eyl": 36,
        "gaalkacyo": 37,
        "galdogob": 38,
        "garbahaarey": 39,
        "garowe": 40,
        "gebiley": 41,
        "hargeisa": 42,
        "hawl wadaag": 43,
        "heliwa": 44,
        "hobyo": 45,
        "hodan": 46,
        "iskushuban": 47,
        "jamaame": 48,
        "jariiban": 49,
        "jowhar": 50,
        "karaan": 51,
        "laas caanod": 52,
        "laasqoray": 53,
        "lughaye": 54,
        "luuq": 55,
        "marka": 56,
        "owdweyne": 57,
        "qandala": 58,
        "qansax dheere": 59,
        "qardho": 60,
        "qoryooley": 61,
        "saakow": 62,
        "sanaag": 63,
        "sheikh": 64,
        "shibis": 65,
        "taleex": 66,
        "waaberi": 67,
        "waajid": 68,
        "wadajir": 69,
        "wanla weyne": 70,
        "wardhiigleey": 71,
        "xamar jaabjab": 72,
        "xudun": 73,
        "xudur": 74,
        "yaaqshid": 75
    }

    urban_rural = {
        Codes.RURAL: 1,
        Codes.URBAN: 2
    }

    yes_no = {
        Codes.NO: 1,
        Codes.YES: 2
    }

    yes_no_both = dict(yes_no)
    yes_no_both["both"] = 3

    gender = {
        Codes.MALE: 1,
        Codes.FEMALE: 2
    }

    radio_station = {
        "radio star": 1,
        "radio mustaqbal": 2,
        "radio risaala": 3,
        "radio dalsan": 4,
        "radio kulminye": 5,
        "radio sooyaal": 6,
        "radio kismayo": 7,
        "radio warsan": 8,
        "radio baidoa": 9,
        "radio hiran_way": 10
    }

    education = {
        "no schooling": 1,
        "primary education": 2,
        "college/university": 3,
        "secondary education": 4,
        "islamic studies": 5
    }

    sickness_adult_child = {
        "child": 1,
        "adult": 2,
        "relative": 3  # TODO: Notify Johanna of difference ('adult and child') in coding scheme
    }

    message_type = {
        "promo": 1,
        "advert": 2,
        "show": 3
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
            # assert False, # TODO: assert message
            pass

    @classmethod
    def apply_missing_code_book(cls, coded_response):
        return cls.missing.get(coded_response, coded_response)
