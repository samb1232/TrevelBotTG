import logging
from sqlite3 import Date

import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, Session

from database.db_base import db_base
from database.tables.users import User


class db_helper:
    @staticmethod
    def get_database_session() -> Session:
        logging.info(f'Создание движка СУБД sqlite3')
        engine = db.create_engine("sqlite:///testdb.db")

        logging.info('Инициализация таблиц')
        db_base.Base.metadata.create_all(engine)

        logging.info('Подключение к базе данных успешно')
        return sessionmaker(bind=engine)()

    session = get_database_session()

    @staticmethod
    def get_user_by_id(user_id: int) -> User | None:
        return db_helper.session.query(User).filter(User.user_id == user_id).first()

    @staticmethod
    def add_new_user(user_id: int, subscription_type: int, subscription_start_date: Date, excursions_left: int) -> None:
        new_user = User(user_id, subscription_type, subscription_start_date, excursions_left)
        db_helper.session.add(new_user)
        db_helper.session.commit()
