from datetime import datetime, timedelta, timezone
import pytz
from config import settings

def isodate_with_delta(from_now: bool = True, **delta):
    if from_now:
        date = datetime.now(timezone.utc) + timedelta(**delta)
    else:
        date = datetime.now(timezone.utc) - timedelta(**delta)

    return date.isoformat()


def isodate_to_timezone(date_str: str, gtm_bias: int = 3):
    if date_str is None:
        return None

    date_obj = datetime.fromisoformat(date_str.split('Z')[0])
    tz = timezone(timedelta(hours=gtm_bias))
    return date_obj.astimezone(tz)


def now():
    return datetime.now().astimezone(pytz.timezone(settings.TIMEZONE))