from utils.sync_utils import handle_item, ID_EXTRACT_PATTERN
import services.google_service as google_service
from models import TasksOrm
from utils.date import isodate_to_timezone
import re


async def handle():
    await handle_item(google_service.get_tasks, TasksOrm, 'task_id', prepare_data)


def prepare_data(item):
    return {
        'title': re.sub(ID_EXTRACT_PATTERN, '', item["title"]),
        'task_id': item["id"],
        'is_completed': item["status"] == 'completed',
        'completed_at': isodate_to_timezone(item.get("completed")),
        'is_hidden': item.get("hidden", False),
        'is_deleted': item.get("deleted", False),
        'due_at': isodate_to_timezone(item["due"]),
    }
