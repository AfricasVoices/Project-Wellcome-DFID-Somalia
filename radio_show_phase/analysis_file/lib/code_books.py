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
        "bacadweyne": 10,
        "badhaadhe": 11,
        "baki": 12,
        "bakool": 13,
        "balad": 14,
        "balcad": 15,
        "banadir": 16,
        "bandarbayla": 17,
        "baraawe": 18,
        "bardera": 19,
        "bari": 20,
        "bay": 21,
        "berbera": 22,
        "berdaale": 23,
        "boondheere": 24,
        "borama": 25,
        "bossaso": 26,
        "bulo burto": 27,
        "bulo marer": 28,
        "burco": 29,
        "burtinle": 30,
        "buuhoodle": 31,
        "buur hakaba": 32,
        "cabdlcasiis": 33,
        "cabudwaaq": 34,
        "cadaado": 35,
        "cadale": 36,
        "caluula": 37,
        "carmo": 38,
        "caynabo": 39,
        "ceel afweyn": 40,
        "ceel buur": 41,
        "ceel dheer": 42,
        "ceel gaal": 43,
        "ceel waaq": 44,
        "ceelasha biyaha": 45,
        "ceerigaabo": 46,
        "dadaab": 47,
        "daynile": 48,
        "dharkenley": 49,
        "dhuusamarreeb": 50,
        "diinsoor": 51,
        "djibouti": 52,
        "dont know": 53,
        "doolow": 54,
        "eyl": 55,
        "gaalkacyo": 56,
        "galdogob": 57,
        "galgaduud": 58,
        "galguduud": 59,
        "galmudug": 60,
        "garbahaarey": 61,
        "garowe": 62,
        "gebiley": 63,
        "gedo": 64,
        "guriceel": 65,
        "hargeisa": 66,
        "hawl wadaag": 67,
        "heliwa": 68,
        "hiran": 69,
        "hobyo": 70,
        "hodan": 71,
        "hudur": 72,
        "iskushuban": 73,
        "jalalaqsi": 74,
        "jamaame": 75,
        "jariiban": 76,
        "jigjiga": 77,
        "jijiga": 78,
        "jilib": 79,
        "jowhar": 80,
        "karaan": 81,
        "laas caanod": 82,
        "lower jubba": 83,
        "lower shabelle": 84,
        "lughaye": 85,
        "luuq": 86,
        "mahadaay": 87,
        "marka": 88,
        "matabaan": 89,
        "maxaas": 90,
        "middle shabelle": 91,
        "mudug": 92,
        "nugaal": 93,
        "nugal": 94,
        "other": 95,
        "owdweyne": 96,
        "qandala": 97,
        "qansax dheere": 98,
        "qardho": 99,
        "qoryooley": 100,
        "saakow": 101,
        "sanaag": 102,
        "shangaani": 103,
        "sheikh": 104,
        "shibis": 105,
        "taleex": 106,
        "tayeeglow": 107,
        "togdheer": 108,
        "waaberi": 109,
        "waajid": 110,
        "wadajir": 111,
        "wanla weyne": 112,
        "wardhiigleey": 113,
        "warsheikh": 114,
        "xamar jaabjab": 115,
        "xamar weyne": 116,
        "xarardheere": 117,
        "xudun": 118,
        "xudur": 119,
        "yaaqshid": 120,
        
        # TODO: Renumber district codes
        "laasqoray": 121
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

    cholera_vaccination = dict(yes_no)
    cholera_vaccination["dont know"] = 3

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
        "hiran_way": 10,
        "bbc": 11,
        "hargeisa": 12,
        "daljir": 13,
        "gal gaduud": 14,
        "ergo": 15,
        "hiran_weyn": 16,
        "alpha": 17,
        "goob joog": 18,
        "dabare": 19,
        "wadaag": 20,
        "shabelle": 21,
        "galkacyo": 22,
        "garowe": 23,
        "sbc": 24,
        "afgoye": 25,
        "jowhar": 26,
        "danan": 27,
        "balcad": 28,
        "voa": 29,
        "knn": 30,
        "wadani": 31,
        "gool": 32,
        "kulmiye": 33,
        "other": 34
    }

    education = {
        "no schooling": 1,
        "primary education": 2,
        "college/university": 3,
        "secondary education": 4,
        "islamic studies": 5,
        "other": 6
    }

    sickness_adult_child = {
        "child": 1,
        "adult": 2,
        "relative": 3,
        "dont know": 4
    }

    message_type = {
        "promo": 1,
        "advert": 2,
        "show": 3,
        "after-last-show": 4
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
