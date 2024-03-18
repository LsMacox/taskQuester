import dateutil.parser
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from orm import ASyncORM
from services.dto.CategoryDTO import CategoryDTO
from typing import Union
from datetime import datetime
import services.google_service as google_service
from dateutil.parser import parse
import pytz
from config import settings
from contextlib import asynccontextmanager
from models import EventsOrm, TasksOrm, CategoryOrm
from sqlalchemy.orm import joinedload
from sqlalchemy import insert
from database import sessionmanager
from dependecies.core import DBSessionDep
import sys
from utils.arguments import parse_arguments
from schemas.Event import Event
from schemas.Task import Task
from schemas.Category import Category
from jobs.sync_google_tasks_job import prepare_data as prepare_task
from jobs.sync_google_events_job import prepare_data as prepare_event


args = parse_arguments(sys.argv)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Function that handles startup and shutdown events.
    To understand more, read https://fastapi.tiangolo.com/advanced/events/
    """
    client_creds, user_creds = await google_service.authenticate()
    settings.GOOGLE_CLIENT_CREDS.update(client_creds)
    settings.GOOGLE_USER_CREDS.update(user_creds)
    yield
    if sessionmanager._engine is not None:
        # Close the DB connection
        await sessionmanager.close()


def parse_date(start_date: str, end_date: Union[str, None] = None):
    tz = pytz.timezone(settings.TIMEZONE)

    try:
        start_date = parse(start_date).astimezone(tz).isoformat()
    except dateutil.parser.ParserError as error:
        raise HTTPException(status_code=422, detail="Incorrect field start_date")

    if not end_date:
        end_date = datetime.now().astimezone(tz).isoformat()
    else:
        end_date = parse(end_date).astimezone(tz).isoformat()

    return start_date, end_date


def create_fastapi_app():
    app = FastAPI(title="FastAPI", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
    )

    @app.get("/categories")
    async def get_categories(db_session: DBSessionDep):
        categories = await ASyncORM.query_items(
            db_session,
            CategoryOrm,
            [CategoryOrm.parent_id != None],
            [joinedload(CategoryOrm.parent)]
        )

        for c in categories:
            c.name = c.parent.name + '_' + c.name

        categories_dto = [Category.model_validate(row, from_attributes=True) for row in categories]

        return categories_dto

    @app.get("/events", tags=["Событии"])
    async def get_events(db_session: DBSessionDep, start_date: str, end_date: str,
                         is_completed: Union[str, None] = None,
                         category_ids: Union[str, None] = None):
        start_date, end_date = parse_date(start_date, end_date)

        conditions = []

        if category_ids is not None:
            categories = category_ids.split(',')
            conditions.append(EventsOrm.categories.any(CategoryOrm.id.in_(categories)))

        if is_completed is not None:
            conditions.append(EventsOrm.is_completed == is_completed)

        if start_date is not None:
            start_date_obj = parse(start_date).strftime("%Y-%m-%d")
            conditions.append(EventsOrm.start_datetime >= start_date_obj)

        if end_date is not None:
            end_date_obj = parse(end_date).strftime("%Y-%m-%d")
            conditions.append(EventsOrm.end_datetime <= end_date_obj)

        events = await ASyncORM.query_items(db_session, EventsOrm, conditions)

        events_dto = [Event.model_validate(row, from_attributes=True) for row in events]

        return events_dto

    @app.post("/events", tags=["Событии"])
    async def create_event(db_session: DBSessionDep, category_id: int, start_date: str,
                           end_date: Union[str, None] = None):
        categories = await ASyncORM.query_items(
            db_session,
            CategoryOrm,
            [CategoryOrm.id == category_id],
            [joinedload(CategoryOrm.parent)]
        )
        category = categories[0]
        parent_category = category.parent

        start_date, end_date = parse_date(start_date, end_date)

        event = await google_service.insert_event(**{
            "summary": '[id=' + str(category.id) + ']: ' + parent_category.name + '_' + category.name,
            "location": "",
            "description": "",
            "start": {
                'dateTime': start_date,
                'timeZone': settings.TIMEZONE,
            },
            "end": {
                "dateTime": end_date,
                "timeZone": settings.TIMEZONE,
            },
            "attendees": [],
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "popup", "minutes": 10}
                ]
            }
        })

    @app.get("/tasks", tags=["Задачи"])
    async def get_tasks(db_session: DBSessionDep, start_date: str, end_date: str,
                        is_completed: Union[str, None] = None,
                        category_ids: Union[str, None] = None):
        start_date, end_date = parse_date(start_date, end_date)

        conditions = []

        if category_ids is not None:
            categories = category_ids.split(',')
            conditions.append(TasksOrm.categories.any(CategoryOrm.id.in_(categories)))

        if is_completed is not None:
            conditions.append(TasksOrm.is_completed == is_completed)

        if start_date is not None:
            start_date_obj = parse(start_date).strftime("%Y-%m-%d")
            conditions.append(TasksOrm.due_at >= start_date_obj)

        if end_date is not None:
            end_date_obj = parse(end_date).strftime("%Y-%m-%d")
            conditions.append(TasksOrm.due_at <= end_date_obj)

        tasks = await ASyncORM.query_items(db_session, TasksOrm, conditions)

        tasks_dto = [Task.model_validate(row, from_attributes=True) for row in tasks]

        return tasks_dto

    @app.post("/tasks", tags=["Задачи"])
    async def create_task(db_session: DBSessionDep, category_id: int, start_date: str):
        categories = await ASyncORM.query_items(
            db_session,
            CategoryOrm,
            [CategoryOrm.id == category_id],
            [joinedload(CategoryOrm.parent)]
        )
        category = categories[0]
        parent_category = category.parent

        start_date, end_date = parse_date(start_date)

        if parent_category:
            title = f'[id={category.id}]: {parent_category.name}_{category.name}'
        else:
            title = f'[id={category.id}]: {category.name}'

        task = await google_service.insert_task(**{
            "title": title,
            "notes": "",
            "due": start_date,
        })


    return app


app = create_fastapi_app()
