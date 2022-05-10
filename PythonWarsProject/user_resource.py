import re

from data.users import User
from flask_restful import Resource, abort
from data import db_session
from flask import jsonify
from user_reqparse import parser


class UserResource(Resource):
    """
    Класс API, предоставляющий функционал работы с пользователями.
    """

    @staticmethod
    def get(user_id: int):
        """
        Получение данных об одном пользователе.
        :parameter user_id: идентификатор пользователя в таблице
        """
        abort_error(user_id)
        ses = db_session.create_session()
        user = ses.query(User).get(user_id)
        return jsonify({'user': user.to_dict(only=('nickname', 'experience', 'created_katas'))})


class UserPostResource(Resource):
    """Класс API, который позволяет добавлять пользователей в таблицу users"""

    @classmethod
    def post(cls):
        """
        Функция, позволяющая добавлять пользователя в базу данных
        """

        session = db_session.create_session()
        arguments = parser.parse_args()

        if session.query(User).filter(User.nickname == arguments['nickname']).first():
            return jsonify({"ERROR": "nickname already taken!"})

        if not cls.__check_email(arguments['email']):
            return jsonify({"ERROR": "invalid email address"})

        user = User(nickname=arguments['nickname'], email=arguments['email'])
        user.set_hashed_password(arguments['pswrd'])
        user.created_katas = user.experience = 0
        session.add(user)
        session.commit()

        return jsonify({"OK": f"SUCCESS"})

    @staticmethod
    def __check_email(email: str) -> bool:
        if re.fullmatch(r'^[^_.-][0-9A-Za-z._-]*@[a-zA-Z]{2,7}\.[A-Za-z-_]{2,7}$', email) and \
                not re.search(r'[^0-9A-Za-z]{2,}', email):
            return True
        return False


class UserListResource(Resource):
    """Класс API, предоставляющий возможность работы со всеми пользователями"""

    @classmethod
    def get(cls, prop: str, lim: int, order: str):
        """
        Функция, отвечающая за получение данных о lim первых пользователях по критерию prop,
        отсортированных в порядке order.
        :parameter prop: отвечает за то, по какому критерию пользователи будут отсортированы.
        :parameter lim: отвечает за то, сколько пользователей будет выведено.
        :parameter order: отвечает за порядок сортировки: htl == asc; lth == desc
        """

        if prop not in ('experience', 'createdKatas'):
            return jsonify({"ERROR": 'Invalid prop value. Possible values: `experience`, `createdKatas`'})

        if order not in ('htl', 'lth'):
            return jsonify({"ERROR": 'Invalid order value. Possible order values: `htl`, `lth`'})

        ses = db_session.create_session()

        if prop == 'createdKatas':
            prop = "created_katas"

        all_users = ses.query(User).order_by(getattr(getattr(User, prop), {'lth': 'asc', 'htl': 'desc'}[order])()).limit(lim).all()

        return jsonify(
            {
                "users":
                    [
                        user.to_dict(only=('nickname', 'experience', 'created_katas'))
                        for user in all_users
                    ]
            }
        )


def abort_error(user_id: int) -> None:
    """Функция, выдающая json-объект с ошибкой 404, если пользователь с ID user_id не был найден"""
    ses = db_session.create_session()
    user = ses.query(User).get(user_id)
    if not user:
        abort(404, message=f'User with id {user_id} not found')