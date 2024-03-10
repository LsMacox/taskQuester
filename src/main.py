import asyncio
import uvicorn
from seeders.category_seeder import seed as seed_category
import sys
from utils.arguments import parse_arguments
from services.google_service import authenticate
from config import settings
from database import sessionmanager
from orm import ASyncORM

args = parse_arguments(sys.argv)


async def main() -> None:
    client_creds, user_creds = await authenticate()

    settings.GOOGLE_CLIENT_CREDS.update(client_creds)
    settings.GOOGLE_USER_CREDS.update(user_creds)

    async with sessionmanager._engine.begin() as db_session:
        if "--create-tables" in args:
            await ASyncORM.create_tables(db_session)
        if "--drop-tables" in args:
            await ASyncORM.drop_tables(db_session)

    if "--seed" in args:
        if args["--seed"] == "category":
            await seed_category()
            raise SystemExit


if __name__ == "__main__":
    asyncio.run(main())

    if "--webserver" in args:
        uvicorn.run(
            app="services.fastapi_app:app",
            host="0.0.0.0",
            port=8000,
        )
