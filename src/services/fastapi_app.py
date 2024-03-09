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
from models import EventsOrm, TasksOrm, CategoryOrm
from sqlalchemy.orm import joinedload


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
    app = FastAPI(title="FastAPI")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
    )

    @app.on_event("startup")
    async def startup_event():
        client_creds, user_creds = await google_service.authenticate()
        settings.GOOGLE_CLIENT_CREDS.update(client_creds)
        settings.GOOGLE_USER_CREDS.update(user_creds)

    @app.get("/categories")
    async def get_categories():
        categories = await ASyncORM.query_items(
            CategoryOrm,
            [CategoryOrm.parent_id != None],
            [joinedload(CategoryOrm.parent)]
        )

        for c in categories:
            c.name = c.parent.name + '_' + c.name

        categories_dto = [CategoryDTO.model_validate(row, from_attributes=True) for row in categories]

        return categories_dto

    @app.get("/events", tags=["Событии"])
    async def get_events(start_date: str, end_date: Union[str, None] = None, is_completed: Union[str, None] = None,
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

        res = await ASyncORM.query_items(EventsOrm, conditions)

        return res

    @app.post("/events", tags=["Событии"])
    async def create_event(category_id: int, start_date: str, end_date: Union[str, None] = None):
        categories = await ASyncORM.query_items(
            CategoryOrm,
            [CategoryOrm.id == category_id],
            [joinedload(CategoryOrm.parent)]
        )
        category = categories[0]
        parent_category = category.parent

        start_date, end_date = parse_date(start_date, end_date)

        try:
            res = await google_service.insert_event(**{
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

            return res
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/tasks", tags=["Задачи"])
    async def get_tasks(start_date: str, is_completed: Union[str, None] = None,
                         category_ids: Union[str, None] = None):
        start_date, end_date = parse_date(start_date)

        conditions = []

        if category_ids is not None:
            categories = category_ids.split(',')
            conditions.append(TasksOrm.categories.any(CategoryOrm.id.in_(categories)))

        if is_completed is not None:
            conditions.append(TasksOrm.is_completed == is_completed)

        if start_date is not None:
            start_date_obj = parse(start_date).strftime("%Y-%m-%d")
            conditions.append(TasksOrm.due_at >= start_date_obj)

        res = await ASyncORM.query_items(TasksOrm, conditions)

        return res

    @app.post("/tasks", tags=["Задачи"])
    async def create_task(category_id: int, start_date: str):
        categories = await ASyncORM.query_items(
            CategoryOrm,
            [CategoryOrm.id == category_id],
            [joinedload(CategoryOrm.parent)]
        )
        category = categories[0]
        parent_category = category.parent

        start_date, end_date = parse_date(start_date)

        try:
            res = await google_service.insert_task(**{
                "title": '[id=' + str(category.id) + ']: ' + parent_category.name + '_' + category.name,
                "notes": "",
                "due": start_date,
            })

            return res
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return app


app = create_fastapi_app()
