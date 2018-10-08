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
        "afgooye": 6,
        "afmadow": 7,
        "awdal": 8,
        "baardheere": 9,
        "badhaadhe": 10,
        "baki": 11,
        "bakool": 12,
        "balad": 13,
        "balcad": 14,
        "banadir": 15,
        "bandarbayla": 16,
        "baraawe": 17,
        "bardera": 18,
        "bari": 19,
        "bay": 20,
        "berbera": 21,
        "berdaale": 22,
        "boondheere": 23,
        "borama": 24,
        "bossaso": 25,
        "bulo burto": 26,
        "bulo marer": 27,
        "burco": 28,
        "burtinle": 29,
        "buuhoodle": 30,
        "buur hakaba": 31,
        "cabdlcasiis": 32,
        "cabudwaaq": 33,
        "cadaado": 34,
        "cadale": 35,
        "caluula": 36,
        "carmo": 37,
        "caynabo": 38,
        "ceel afweyn": 39,
        "ceel buur": 40,
        "ceel waaq": 41,
        "ceelasha biyaha": 42,
        "ceerigaabo": 43,
        "daynile": 44,
        "dharkenley": 45,
        "dhuusamarreeb": 46,
        "diinsoor": 47,
        "djibouti": 48,
        "dont know": 49,
        "doolow": 50,
        "eyl": 51,
        "gaalkacyo": 52,
        "galdogob": 53,
        "galgaduud": 54,
        "galguduud": 55,
        "galmudug": 56,
        "garbahaarey": 57,
        "garowe": 58,
        "gebiley": 59,
        "gedo": 60,
        "guriceel": 61,
        "hargeisa": 62,
        "hawl wadaag": 63,
        "heliwa": 64,
        "hiran": 65,
        "hodan": 66,
        "hudur": 67,
        "iskushuban": 68,
        "jalalaqsi": 69,
        "jamaame": 70,
        "jariiban": 71,
        "jigjiga": 72,
        "jijiga": 73,
        "jilib": 74,
        "jowhar": 75,
        "karaan": 76,
        "laas caanod": 77,
        "lower jubba": 78,
        "lower shabelle": 79,
        "lughaye": 80,
        "luuq": 81,
        "mahadaay": 82,
        "marka": 83,
        "matabaan": 84,
        "maxaas": 85,
        "middle shabelle": 86,
        "mudug": 87,
        "nugaal": 88,
        "nugal": 89,
        "other": 90,
        "owdweyne": 91,
        "qandala": 92,
        "qansax dheere": 93,
        "qardho": 94,
        "qoryooley": 95,
        "saakow": 96,
        "sanaag": 97,
        "shangaani": 98,
        "sheikh": 99,
        "shibis": 100,
        "taleex": 101,
        "tayeeglow": 102,
        "togdheer": 103,
        "waaberi": 104,
        "waajid": 105,
        "wadajir": 106,
        "wanla weyne": 107,
        "wardhiigleey": 108,
        "warsheikh": 109,
        "xamar jaabjab": 110,
        "xamar weyne": 111,
        "xarardheere": 112,
        "xudun": 113,
        "xudur": 114,
        "yaaqshid": 115
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
        "star": 1,
        "mustaqbal": 2,
        "risaala": 3,
        "dalsan": 4,
        "kulminye": 5,
        "sooyaal": 6,
        "kismayo": 7,
        "warsan": 8,
        "baidoa": 9,
        "hiran_way": 10
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
