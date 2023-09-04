import sqlalchemy as db
from database.db_base import db_base


class User(db_base.Base):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    subscription_type = db.Column(db.Integer)
    subscription_end_date = db.Column(db.Date)
    excursions_left = db.Column(db.Integer)
