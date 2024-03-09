from aiogoogle import Aiogoogle
from aiogoogle.auth.creds import ServiceAccountCreds, ClientCreds, UserCreds
import aiofiles
import json
from config import settings
from async_lru import alru_cache
from utils.date import isodate_with_delta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


creds = {
    "client_creds": settings.GOOGLE_CLIENT_CREDS,
    "user_creds": settings.GOOGLE_USER_CREDS
}


@alru_cache(maxsize=1)
async def load_credentials(file_path):
    async with aiofiles.open(file_path, 'r') as file:
        content = await file.read()
        return json.loads(content)


async def get_credentials():
    credentials_data = await load_credentials(settings.BASE_DIR / 'assets' / 'service_account_google_cred.json')
    service_account_creds = ServiceAccountCreds(
        scopes=[
            'https://www.googleapis.com/auth/calendar'
        ],
        **credentials_data
    )
    return service_account_creds


async def authenticate():
    SCOPES = [
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/tasks'
    ]

    creds = None

    if (settings.BASE_DIR / 'assets' / 'oauth2_google_creds.json').exists():
        creds = Credentials.from_authorized_user_file(settings.BASE_DIR / 'assets' / 'oauth2_google_creds.json')

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(settings.BASE_DIR / 'assets' / 'oauth2_google_client.json', SCOPES)
            creds = flow.run_local_server(port=0)

            with open(settings.BASE_DIR / 'assets' / 'oauth2_google_creds.json', "w") as token:
                token.write(creds.to_json())

    client_creds = ClientCreds(
        client_id=creds.client_id,
        client_secret=creds.client_secret,
        scopes=creds.scopes
    )

    user_creds = UserCreds(
        refresh_token=creds.refresh_token
    )

    return client_creds, user_creds



async def get_calendar_list(
    calendar_id=settings.GOOGLE_CALENDAR_ID
):
    async with Aiogoogle(**creds) as aiogoogle:
        calendar = await aiogoogle.discover("calendar", "v3")
        res = await aiogoogle.as_user(
            calendar.calendarList.list(calendarId=calendar_id)
        )

        return res


async def get_events(
    calendar_id=settings.GOOGLE_CALENDAR_ID,
    timeMin=isodate_with_delta(from_now=False, weeks=1),
    timeMax=isodate_with_delta(weeks=1)
):
    async with Aiogoogle(**creds) as aiogoogle:
        calendar = await aiogoogle.discover("calendar", "v3")
        res = await aiogoogle.as_user(
            calendar.events.list(calendarId=calendar_id,
                                 timeMin=timeMin,
                                 timeMax=timeMax)
        )

        return res


async def insert_event(
    calendar_id=settings.GOOGLE_CALENDAR_ID,
    **body
):
    async with Aiogoogle(**creds) as aiogoogle:
        calendar = await aiogoogle.discover("calendar", "v3")
        res = await aiogoogle.as_user(
            calendar.events.insert(calendarId=calendar_id, json=body)
        )

    return res


async def get_tasks_list():
    async with Aiogoogle(**creds) as aiogoogle:
        calendar = await aiogoogle.discover("tasks", "v1")
        res = await aiogoogle.as_user(
            calendar.tasklists.list()
        )

        return res


async def get_tasks(
    tasklist=settings.GOOGLE_TASK_LIST,
    timeMin=isodate_with_delta(from_now=False, weeks=1),
    timeMax=isodate_with_delta(weeks=1)
):
    async with Aiogoogle(**creds) as aiogoogle:
        calendar = await aiogoogle.discover("tasks", "v1")
        res = await aiogoogle.as_user(
            calendar.tasks.list(
                tasklist=tasklist,
                dueMin=timeMin,
                dueMax=timeMax,
                showHidden=True,
                showCompleted=True,
                showDeleted=True,
                maxResults=100
            )
        )

        return res


async def insert_task(
    tasklist=settings.GOOGLE_TASK_LIST,
    **body
):
    async with Aiogoogle(**creds) as aiogoogle:
        calendar = await aiogoogle.discover("tasks", "v1")
        res = await aiogoogle.as_user(
            calendar.tasks.insert(tasklist=tasklist, json=body)
        )

    return res

