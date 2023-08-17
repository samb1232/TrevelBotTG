import sqlalchemy as db

from database.db_base import db_base


class Excursion_test(db_base.Base):
    __tablename__ = 'excursion_test'
    user_id = db.Column("user_id", db.Integer, primary_key=True)
    progress = db.Column("progress", db.Integer)

    def __init__(self, user_id, progress):
        self.user_id = user_id
        self.progress = progress
