from orm import ASyncORM
from models import CategoryOrm
from database import sessionmanager, get_db_session


async def seed():
    main_categories = ['language', 'books', 'sport', 'programming', 'other']
    main_categories = [{"name": name, "description": "Главная категория"} for name in main_categories]

    async with sessionmanager.session() as db_session:
        await ASyncORM.upsert_items(db_session, main_categories, CategoryOrm)

        categories = await ASyncORM.query_items(db_session, CategoryOrm)

        sub_categories = [
            {
                "name": 'jump_rope',
                "description": "Прыжки на скакалке",
                "parent_id": get_category_id(categories, 'sport'),
            },
            {
                "name": 'gym',
                "description": "Тренировечные дни с заметкой каким видом тренировок будем заниматься",
                "parent_id": get_category_id(categories, 'sport'),
            },
            {
                "name": 'english_repeat_words',
                "description": "Повторение слов",
                "parent_id": get_category_id(categories, 'language'),
            },
            {
                "name": 'english_repeat_grammar',
                "description": "Повторение грамматики",
                "parent_id": get_category_id(categories, 'language'),
            },
            {
                "name": 'english_repeat_retailing',
                "description": "Повторение пересказов",
                "parent_id": get_category_id(categories, 'language'),
            },
            {
                "name": 'eha_buysanash',
                "description": "Этапы чтение книги Еха бьусанаш (на чеченском)",
                "parent_id": get_category_id(categories, 'books'),
            },
            {
                "name": 'linux_drivers',
                "description": "Этапы чтение книги Драйверы linux",
                "parent_id": get_category_id(categories, 'books'),
            },
            {
                "name": 'leetcode_problem_solving',
                "description": "Решение алгоритмических задач на платформе leetcode",
                "parent_id": get_category_id(categories, 'programming'),
            },
            {
                "name": 'theme',
                "description": "Прохождение разных тем связанных с программированием",
                "parent_id": get_category_id(categories, 'programming'),
            },
        ]

        await ASyncORM.upsert_items(db_session, sub_categories, CategoryOrm)

        await db_session.commit()


def get_category_id(categories, name):
    return [c for c in categories if c.name == name][0].id
