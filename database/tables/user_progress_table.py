import sqlalchemy as db

from database.db_base import db_base


class UserProgress(db_base.Base):
    __tablename__ = 'user_progress'

    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    excursion_name = db.Column(db.String, primary_key=True)
    progress = db.Column(db.Integer)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'excursion_name', name='unique_user_excursion_progress'),
    )
