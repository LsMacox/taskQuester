import re
from orm import ASyncORM
from models import CategoryOrm
from database import sessionmanager

ID_EXTRACT_PATTERN = r'\[id=(\d+)\]: '


async def handle_item(get_items, item_type_orm, item_id_key, prepare_func):
    items = await get_items()

    async with sessionmanager.session() as db_session:
        for item in items['items']:
            title = item.get("summary") or item.get("title")
            match = re.search(ID_EXTRACT_PATTERN, title)

            if match:
                category_id = int(match.group(1))

                item_data = prepare_func(item)
                await ASyncORM.upsert_items(db_session, [item_data], item_type_orm)

                categories = await ASyncORM.query_items(db_session, CategoryOrm, conditions=[CategoryOrm.id == category_id])
                orm_item_condition = getattr(item_type_orm, item_id_key) == item["id"]
                orm_items = await ASyncORM.query_items(db_session, item_type_orm, conditions=[orm_item_condition])

                orm_item = orm_items[0]
                category = categories[0]

                if category not in orm_item.categories:
                    orm_item.categories.append(category)
                    await db_session.merge(orm_item)

        await db_session.commit()
