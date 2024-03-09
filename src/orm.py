from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload
from database import async_engine, async_session_factory, Base
from sqlalchemy.dialects.mysql import insert
from models import CategoryOrm
from typing import List, Type


class ASyncORM:
    @staticmethod
    async def create_tables():
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @staticmethod
    async def drop_tables():
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    @staticmethod
    async def upsert_items(items: List[dict], model: Type[Base]):
        async with async_session_factory() as session:
            for item in items:
                stmt = insert(model).values(**item)
                update_stmt = stmt.on_duplicate_key_update(**item)
                await session.execute(update_stmt)
            await session.commit()

    @staticmethod
    async def query_items(model: Type[Base], conditions: List = None, options: List = None):
        if conditions is None:
            conditions = []
        if options is None:
            options = [selectinload('*')]

        async with async_session_factory() as session:
            query = select(model).options(*options)
            for condition in conditions:
                query = query.where(condition)
            result = await session.execute(query)

        return result.scalars().all()

    @staticmethod
    async def get_category_by(category_id: int, name: str = None, parent_id: int = None):
        conditions = [CategoryOrm.id == category_id]


        if name:
            conditions.append(CategoryOrm.name.contains(name))
        if parent_id is not None:
            conditions.append(CategoryOrm.parent_id == parent_id)
        return await ASyncORM.query_items(CategoryOrm, conditions, options=[joinedload(CategoryOrm.parent)])