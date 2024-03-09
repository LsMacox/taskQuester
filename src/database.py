import asyncio
from typing_extensions import Annotated
from sqlalchemy import text, URL, String, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from config import settings

async_engine = create_async_engine(
    url=settings.DATABASE_URL_asyncmy,
    echo=False,
)

async_session_factory = async_sessionmaker(async_engine)

str_256 = Annotated[str, 256]


class Base(DeclarativeBase):
    type_annotation_map = {
        str_256: String(256)
    }

    # def __repr__(self):
    #     """Relationships не используются в repr(), т.к. могут вести к неожиданным подгрузкам"""
    #     cols = []
    #     for idx, col in enumerate(self.__table__.columns.keys()):
    #         if col in self.repr_cols or idx < self.repr_cols_num:
    #             cols.append(f"{col}={getattr(self, col)}")
    #
    #     return f"<{self.__class__.__name__} {', '.join(cols)}>"
