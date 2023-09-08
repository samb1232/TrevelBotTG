import logging
from sqlite3 import Date

import sqlalchemy as db
from sqlalchemy.orm import sessionmaker, Session

import config
from database.db_base import db_base
from database.tables.user_progress_table import UserProgress
from database.tables.users_table import User

logger = logging.getLogger(__name__)


class db_helper:
    @staticmethod
    def get_database_session() -> Session:
        logger.debug("Подключение к базе данных")
        engine = db.create_engine(config.DATABASE_ENGINE)

        db_base.Base.metadata.create_all(engine)

        return sessionmaker(bind=engine)()

    session = get_database_session()

    @staticmethod
    def get_user_by_id(user_id: int) -> User | None:
        logger.debug(f"Получение пользователя с id = {user_id}")
        return db_helper.session.query(User).filter(User.user_id == user_id).first()

    @staticmethod
    def add_new_user(user_id: int, subscription_type: int, subscription_end_date: Date, excursions_left: int) -> None:
        logger.debug(f"Добавление нового пользователя с id = {user_id}")
        new_user = User(user_id=user_id, subscription_type=subscription_type,
                        subscription_end_date=subscription_end_date, excursions_left=excursions_left)
        db_helper.session.add(new_user)
        db_helper.session.commit()

    @staticmethod
    def set_subscription_to_user(user_id: int, subscription_type: int, subscription_end_date: Date,
                                 excursions_left: int):
        logger.debug(f"Установка пользователю с id = {user_id} подписки по тарифу №{subscription_type}")
        user = db_helper.get_user_by_id(user_id)
        user.subscription_type = subscription_type
        user.subscription_end_date = subscription_end_date
        user.excursions_left = excursions_left
        db_helper.session.commit()

        #  TODO: сделать оповещение пользователя об окончании действия подписки

    @staticmethod
    def decrease_excursions_left(user_id: int) -> bool:
        logger.debug(f"Уменьшение доступных экскурсий пользователя с id = {user_id}")
        user = db_helper.get_user_by_id(user_id)
        if user.excursions_left > 0:
            user.excursions_left -= 1
            db_helper.session.commit()
            return True
        return False

    @staticmethod
    def get_user_progress_on_excursion_by_id(user_id: int, excursion_name: str) -> UserProgress | None:
        logger.debug(f"Получение прогресса экскурсии \"{excursion_name}\" у пользователя с id = {user_id}")
        user_progress = db_helper.session.query(UserProgress).filter(UserProgress.user_id == user_id).filter(UserProgress.excursion_name == excursion_name).first()
        if user_progress is not None:
            logger.debug(f"Given excursion: {excursion_name}, Real excursion: {user_progress.excursion_name}, progress: {user_progress.progress}")
        return user_progress

    @staticmethod
    def add_user_to_excursion(user_id: int, excursion_name: str) -> None:
        if db_helper.get_user_progress_on_excursion_by_id(user_id, excursion_name) is not None:
            return  # Можно вызвать предупреждение о попытке добавления существующего пользователя
        logger.debug(f"Добавление пользователя с id = {user_id} в экскурсию \"{excursion_name}\"")
        new_user_progress = UserProgress(user_id=user_id, excursion_name=excursion_name, progress=0)
        db_helper.session.add(new_user_progress)
        db_helper.session.commit()
        db_helper.decrease_excursions_left(user_id)

    @staticmethod
    def increase_progress_excursion(user_id: int, excursion_name: str):
        logger.debug(f"Инкремент прогресса экскурсии \"{excursion_name}\" для пользователя с id = {user_id}")
        user_progress = db_helper.get_user_progress_on_excursion_by_id(user_id, excursion_name)
        user_progress.progress += 1
        db_helper.session.commit()

    @staticmethod
    def decrease_progress_excursion(user_id: int, excursion_name: str):
        logger.debug(f"Декремент прогресса экскурсии \"{excursion_name}\" для пользователя с id = {user_id}")
        user_progress = db_helper.get_user_progress_on_excursion_by_id(user_id, excursion_name)
        user_progress.progress -= 1
        db_helper.session.commit()

    @staticmethod
    def reset_user_progress_for_excursion(user_id: int, excursion_name: str):
        logger.debug(f"Сброс прогресса экскурсии \"{excursion_name}\" для пользователя с id = {user_id}")
        user_progress = db_helper.get_user_progress_on_excursion_by_id(user_id, excursion_name)
        user_progress.progress = 0
        db_helper.session.commit()
