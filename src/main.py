import asyncio
import uvicorn
from seeders.category_seeder import seed as seed_category
import sys
from utils.arguments import parse_arguments
from database import Base, sync_engine

args = parse_arguments(sys.argv)


def main() -> None:
    if "--create-tables" in args:
        Base.metadata.create_all(sync_engine)
        raise SystemExit
    if "--drop-tables" in args:
        Base.metadata.drop_all(sync_engine)
        raise SystemExit

    if "--seed" in args:
        if args["--seed"] == "category":
            asyncio.run(seed_category())
            raise SystemExit


if __name__ == "__main__":
    main()

    if "--webserver" in args:
        uvicorn.run(
            app="services.fastapi_app:app",
            host="0.0.0.0",
            port=8000,
        )
