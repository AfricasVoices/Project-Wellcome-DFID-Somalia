import time

import pytz  # Timezone library for converting datetime objects between timezones
from core_data_modules.cleaners import Codes
from core_data_modules.traced_data import Metadata
from dateutil.parser import isoparse

class AnalysisKeys(object):
    # TODO: Move some of these methods to Core Data?

    @staticmethod
    def get_date_time_utc(td):
        return isoparse(td["created_on"]).strftime("%Y-%m-%d %H:%M")

    @staticmethod
    def get_date_time_eat(td):
        return isoparse(td["created_on"]).astimezone(pytz.timezone("Africa/Nairobi")).strftime("%Y-%m-%d %H:%M")

    @staticmethod
    def set_matrix_keys(user, data, all_matrix_keys, code_scheme_name, code_ids, coded_key, matrix_prefix=""):
        for td in data:
            matrix_d = dict()

            for label in td.get(coded_key, []):
                matrix_d[f"{matrix_prefix}{code_ids[code_scheme_name][label['CodeID']]}"] = Codes.MATRIX_1
                
            for key in all_matrix_keys:
                if key not in matrix_d:
                    matrix_d[key] = Codes.MATRIX_0

            td.append_data(matrix_d, Metadata(user, Metadata.get_call_location(), time.time()))

    @staticmethod
    def set_analysis_keys(user, data, key_map):
        for td in data:
            td.append_data(
                {new_key: td[old_key] for new_key, old_key in key_map.items()},
                Metadata(user, Metadata.get_call_location(), time.time())
            )
