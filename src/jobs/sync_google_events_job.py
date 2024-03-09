from utils.sync_utils import handle_item, ID_EXTRACT_PATTERN
import services.google_service as google_service
from models import EventsOrm
from utils.date import isodate_to_timezone, now
import re


async def handle():
    await handle_item(google_service.get_events, EventsOrm, 'event_id', prepare_data)


def prepare_data(item):
    start_date = isodate_to_timezone(item["start"]["dateTime"])

    return {
        'title': re.sub(ID_EXTRACT_PATTERN, '', item["summary"]),
        'event_id': item["id"],
        'is_completed': item["status"] == 'confirmed' or start_date > now,
        'start_datetime': start_date,
        'end_datetime': isodate_to_timezone(item["end"]["dateTime"]),
    }
