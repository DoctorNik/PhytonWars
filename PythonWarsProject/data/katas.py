import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Kata(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = "katas"
    id = sqlalchemy.Column(sqlalchemy.Integer, autoincrement=True, unique=True, primary_key=True)
    title = sqlalchemy.Column(sqlalchemy.String, unique=True)
    author_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    description = sqlalchemy.Column(sqlalchemy.String)
    completed_solution = sqlalchemy.Column(sqlalchemy.String)
    tests = sqlalchemy.Column(sqlalchemy.String)
    total_solutions = sqlalchemy.Column(sqlalchemy.Integer)
    total_successful_solutions = sqlalchemy.Column(sqlalchemy.Integer)
    difficulty = sqlalchemy.Column(sqlalchemy.Integer)
