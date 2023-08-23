import logging
from sqlite3 import Date

import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, Session

from database.db_base import db_base
from database.tables.users import User

logger = logging.getLogger(__name__)


class db_helper:
    @staticmethod
    def get_database_session() -> Session:
        logger.info("Подключение к базе данных")
        engine = db.create_engine("sqlite:///testdb.db")

        db_base.Base.metadata.create_all(engine)

        return sessionmaker(bind=engine)()

    session = get_database_session()

    @staticmethod
    def get_user_by_id(user_id: int) -> User | None:

        logger.info(f"Получение пользователя с id = {user_id} из базы данных")
        return db_helper.session.query(User).filter(User.user_id == user_id).first()

    @staticmethod
    def add_new_user(user_id: int, subscription_type: int, subscription_start_date: Date, excursions_left: int) -> None:
        new_user = User(user_id, subscription_type, subscription_start_date, excursions_left)
        db_helper.session.add(new_user)
        db_helper.session.commit()
