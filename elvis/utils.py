from datetime import datetime
import pytz

DATE_PREFIX = '/Date('
DATE_SUFFIX = ')/'

ELVIS_TIMEZONE = pytz.timezone('Europe/Tallinn')
UTC = pytz.timezone('UTC')


def decode_elvis_timestamp(timestamp: str):
    """Try to convert the argument to timestamp using ELVIS rules, return it unmodified if impossible"""
    str_timestamp = str(timestamp).strip()
    if str_timestamp.startswith(DATE_PREFIX) and str_timestamp.endswith(DATE_SUFFIX):
        milliseconds = str_timestamp[len(DATE_PREFIX):-len(DATE_SUFFIX)]
        timezone_offset = 0
        try:
            if "+" in milliseconds:
                timezone_offset_string = milliseconds[milliseconds.index("+")+1:]
                milliseconds = milliseconds[:milliseconds.index("+")]
                if len(timezone_offset_string) == 4:
                    timezone_offset = int(timezone_offset_string[:2])*60+int(timezone_offset_string[2:])
            seconds = int(milliseconds) / 1000
        except ValueError:
            return timestamp

        # Elvis Timezone offsets are relevant to Elvis natural timezone (Tallinn)
        return ELVIS_TIMEZONE.localize(datetime.fromtimestamp(seconds).astimezone(
            pytz.FixedOffset(-timezone_offset)
        ).replace(tzinfo=None))

    return timestamp
