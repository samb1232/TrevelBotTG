import logging
from sqlite3 import Date

import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, Session

import config
from database.db_base import db_base
from database.tables.excursion_test import Excursion_test
from database.tables.users import User

logger = logging.getLogger(__name__)


class db_helper:
    @staticmethod
    def get_database_session() -> Session:
        logger.info("Подключение к базе данных")
        engine = db.create_engine(config.DATABASE_ENGINE)

        db_base.Base.metadata.create_all(engine)

        return sessionmaker(bind=engine)()

    session = get_database_session()

    @staticmethod
    def get_user_by_id(user_id: int) -> User | None:
        return db_helper.session.query(User).filter(User.user_id == user_id).first()

    @staticmethod
    def get_excursion_info_by_id(user_id: int) -> Excursion_test | None:
        return db_helper.session.query(Excursion_test).filter(Excursion_test.user_id == user_id).first()

    @staticmethod
    def add_new_user(user_id: int, subscription_type: int, subscription_end_date: Date, excursions_left: int) -> None:
        new_user = User(user_id, subscription_type, subscription_end_date, excursions_left)
        db_helper.session.add(new_user)
        db_helper.session.commit()

    @staticmethod
    def decrease_excursions_left(user_id: int) -> bool:
        user = db_helper.get_user_by_id(user_id)
        if user.excursions_left > 0:
            user.excursions_left -= 1
            db_helper.session.commit()
            return True
        return False

    @staticmethod
    def add_user_to_excursion(user_id: int, excursion_class) -> None:
        new_user = excursion_class(user_id=user_id, progress=0)
        db_helper.session.add(new_user)
        db_helper.session.commit()

    @staticmethod
    def increase_progress_excursion_test(user_id: int):
        excursion = db_helper.get_excursion_info_by_id(user_id)
        excursion.progress += 1
        db_helper.session.commit()

    @staticmethod
    def decrease_progress_excursion_test(user_id: int):
        excursion = db_helper.get_excursion_info_by_id(user_id)
        excursion.progress -= 1
        db_helper.session.commit()

    @staticmethod
    def reset_progress_excursion_test(user_id: int):
        excursion = db_helper.get_excursion_info_by_id(user_id)
        excursion.progress = 0
        db_helper.session.commit()
