import asyncio
import uvicorn
from seeders.category_seeder import seed as seed_category
from orm import ASyncORM
import sys
from utils.arguments import parse_arguments
from services.google_service import authenticate
from config import settings
from database import async_engine

args = parse_arguments(sys.argv)


async def main() -> None:
    client_creds, user_creds = await authenticate()

    settings.GOOGLE_CLIENT_CREDS.update(client_creds)
    settings.GOOGLE_USER_CREDS.update(user_creds)

    if "--echo" in args:
        async_engine.echo = True

    if "--seed" in args:
        if args["--seed"] == "category":
            await seed_category()
            raise SystemExit

    if "--drop" in args:
        await ASyncORM.drop_tables()

    await ASyncORM.create_tables()


if __name__ == "__main__":
    # asyncio.run(main())

    ssl_context = {}
    port = 8000

    if not settings.DEBUG:
        ssl_context = {
            "ssl_certfile": settings.BASE_DIR / 'contrib' / 'ssl' / 'cert.pem',
            "ssl_keyfile": settings.BASE_DIR / 'contrib' / 'ssl' / 'key.pem',
        }
        port = 443

    if "--webserver" in args:
        uvicorn.run(
            app="services.fastapi_app:app",
            host="0.0.0.0",
            port=8000,
            # **ssl_context,
        )
