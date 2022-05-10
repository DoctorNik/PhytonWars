from data.users import User
from data.katas import Kata
from flask_restful import Resource, abort
from data import db_session
from flask import jsonify


class KataResource(Resource):
    """Класс API, отвечающий за работу с одной задачей"""

    @classmethod
    def get(cls, kata_id: int):
        """
        Получение данных об одной задаче
        :parameter kata_id: отвечает за id задачи
        """
        abort_error(kata_id)
        ses = db_session.create_session()
        kata = ses.query(Kata).filter(Kata.id == kata_id).first()
        user = ses.query(User).filter(User.id == kata.author_id).first()
        return jsonify({"kata": {'author': user.nickname} |
                                kata.to_dict(only=('title', "total_solutions",
                                                   "total_successful_solutions", "difficulty"))})


class KataListResource(Resource):
    """Класс API, отвечающий за работу с задачами"""

    @classmethod
    def get(cls, prop: str, lim: int, order: str):
        """
        Получение данных о первых lim' задачах по prop, отсортированных по order
        :parameter prop: отвечает за то, по какому критерию будет сортировка.
        :parameter lim: отвечает за кол-во задач, которые будут выведены в конечном итоге.
        :parameter order: отвечает за порядок сортировки: htl - от большего к меньшему,
                                                          lth - от меньшего к большему
        """
        if prop not in ('difficulty', 'totalSolutions', 'totalSuccessSolutions'):
            return jsonify(
                {
                    "ERROR":
                        "invalid prop value. Possible values: `difficulty`, `totalSolutions`, `totalSuccessSolutions`"
                }
            )

        if not order in ('htl', 'lth'):
            return jsonify(
                {
                    "ERROR":
                        "invalid order value. Possible order values: `lth`, `htl`"
                }
            )

        sess = db_session.create_session()

        # Тут находятся все задачи (количество равно lim, критерий выборки - prop, сортировка - order)
        all_katas = sess.query(Kata).order_by(getattr(getattr(Kata,
                                                              {'difficulty': 'difficulty',
                                                               'totalSuccessSolutions': "total_successful_solutions",
                                                               'total_solutions': 'total_solutions'}.get(prop)),
                                                      {"htl": 'desc', 'lth': 'asc'}[order])()).limit(lim).all()

        return jsonify(
            {
                "katas":
                    [
                        {'author': sess.query(User).get(kata.author_id).nickname} |
                        kata.to_dict(only=('title', 'difficulty', "total_successful_solutions", "total_solutions"))
                        for kata in all_katas
                    ]
            }
        )


def abort_error(kata_id: int) -> None:
    """Функция, выдающая json-объект с ошибкой 404, если задача с ID kata_id была не найдена"""
    ses = db_session.create_session()
    kata = ses.query(Kata).get(kata_id)
    if not kata:
        abort(404, message=f"Kata with id {kata_id} not found")
