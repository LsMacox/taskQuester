from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload
from database import Base, sessionmanager
from sqlalchemy.dialects.mysql import insert
from models import CategoryOrm
from typing import List, Type
from sqlalchemy.ext.asyncio import AsyncSession


class ASyncORM:
    @staticmethod
    async def create_tables(db_session: AsyncSession):
        await db_session.run_sync(Base.metadata.create_all)

    @staticmethod
    async def drop_tables(db_session: AsyncSession):
        await db_session.run_sync(Base.metadata.drop_all)

    @staticmethod
    async def upsert_items(db_session: AsyncSession, items: List[dict], model: Type[Base]):
        for item in items:
            stmt = insert(model).values(**item)
            update_stmt = stmt.on_duplicate_key_update(**item)

            await db_session.execute(update_stmt)

    @staticmethod
    async def query_items(db_session: AsyncSession, model: Type[Base], conditions: List = None, options: List = None):
        if conditions is None:
            conditions = []
        if options is None:
            options = [selectinload('*')]

        query = select(model).options(*options)

        for condition in conditions:
            query = query.where(condition)

        res = await db_session.scalars(query)

        return res.all()

    @staticmethod
    async def get_category_by(db_session: AsyncSession, category_id: int, name: str = None, parent_id: int = None):
        conditions = [CategoryOrm.id == category_id]

        if name:
            conditions.append(CategoryOrm.name.contains(name))
        if parent_id is not None:
            conditions.append(CategoryOrm.parent_id == parent_id)

        return await ASyncORM.query_items(db_session, CategoryOrm, conditions, options=[joinedload(CategoryOrm.parent)])