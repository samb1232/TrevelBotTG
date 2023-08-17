import sqlalchemy as db

from database.db_base import db_base


class User(db_base.Base):
    __tablename__ = 'users'
    user_id = db.Column("user_id", db.Integer, primary_key=True)
    subscription_type = db.Column("subscription_type", db.Integer)
    subscription_start_date = db.Column("subscription_start_date", db.Date)
    excursions_left = db.Column("excursions_left", db.Integer)

    def __init__(self, user_id, subscription_type, subscription_start_date, excursions_left):
        self.user_id = user_id
        self.subscription_type = subscription_type
        self.subscription_start_date = subscription_start_date
        self.excursions_left = excursions_left

    def __repr__(self):
        return (f"User: user_id: {self.user_id}, "
                f"subscription_type: {self.subscription_type}, "
                f"subscription_start_date: {self.subscription_start_date}, "
                f"excursions_left: {self.excursions_left}.")
