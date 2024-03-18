import sys
from jobs.sync_google_events_job import handle as get_events_job
from jobs.sync_google_tasks_job import handle as get_tasks_job
import aioschedule as schedule
import asyncio
from config import settings
from utils.arguments import parse_arguments
from services.google_service import authenticate
from database import sessionmanager


args = parse_arguments(sys.argv)

async def main():
    client_creds, user_creds = await authenticate()

    settings.GOOGLE_CLIENT_CREDS.update(client_creds)
    settings.GOOGLE_USER_CREDS.update(user_creds)

    if "--echo" in args:
        sessionmanager._engine.echo = True

    if "--sync" in args:
        if args["--sync"] == "events":
            await get_events_job()
            raise SystemExit
        elif args["--sync"] == "tasks":
            await get_tasks_job()
            raise SystemExit

    schedule.every().hours.do(get_events_job())
    schedule.every().hours.do(get_tasks_job())

    while True:
        await schedule.run_pending()
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
