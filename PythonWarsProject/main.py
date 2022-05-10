import math
import os
import pathlib
import shutil
from datetime import datetime

from flask import Flask, redirect, render_template, jsonify, Blueprint, request
from flask_restful import Api
from flask_login import login_required, LoginManager, login_user, logout_user, current_user

from forms.login_form import FormLogin
from forms.create_task_form import FormCreateTask
from forms.register_form import FormRegister
from forms.solve_form import SolveKata

from task_resource import KataResource, KataListResource
from user_resource import UserListResource, UserResource, UserPostResource
from data import db_session

from data.users import User
from data.katas import Kata

import subprocess as sp
import re

from settings import *


app = Flask(__name__)
api = Api(app)
app.secret_key = 'Quick brown fox jumps over the lazy dog'

api.add_resource(KataResource, "/api/kata/<int:kata_id>")
api.add_resource(UserResource, "/api/user/<int:user_id>")
api.add_resource(KataListResource, '/api/katas/<string:prop>/<int:lim>/<string:order>')
api.add_resource(UserListResource, "/api/users/<string:prop>/<int:lim>/<string:order>")
api.add_resource(UserPostResource, "/api/postuser")

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(id_):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(id_)


def function_exists(text: str) -> bool:
    """Функция, проверяющая, существует ли функция в коде автора"""
    return bool(re.compile(r'def [a-z]|[a-z] *= *lambda.+: *[^\s]+', flags=re.I).search(text))


def check_email(email: str) -> bool:
    """Функция, проверяющая валидность адреса"""
    if re.fullmatch(r'^[^_.-][0-9A-Za-z._-]*@[a-zA-Z]{2,7}\.[A-Za-z-_]{2,7}$', email) and \
            not re.search(r'[^0-9A-Za-z]{2,}', email):
        return True
    return False


def get_unique_foldername() -> str:
    """Функция, возвращающая имя уникальной директории"""
    return "{}{}".format(current_user.nickname, ''.join(re.findall(r'\d', datetime.now().__str__())))


def delete_past_catalogs():
    """Функция, удаляющая созданные каталоги для создания и решения задач"""
    for current_catalog in os.listdir():
        if str(current_catalog).startswith(current_user.nickname) and re.search(r'\d{8}$', current_catalog):
            shutil.rmtree(os.path.join(pathlib.Path.cwd(), current_catalog), ignore_errors=True)


def check_file_output(current_unique_folder_name: str, solution_fn: str,
                      solution_data: str, test_fn: str, test_data: str) -> (str, None):
    """Функция, создающая уникальную директорию для создания или решения"""

    os.makedirs(current_unique_folder_name)

    with open(os.path.join(current_unique_folder_name, solution_fn), mode='wt', encoding="UTF-8") as solution_file:
        solution_file.write(solution_data)

    with open(os.path.join(current_unique_folder_name, test_fn), mode='w', encoding="UTF-8") as tests_file:
        tests_file.write(test_data)

    result = sp.run(["python", f"{current_unique_folder_name}/{test_fn}"], text=True, capture_output=True)
    stdout = result.stdout
    stderr = re.sub(r'(\(.+\))$', '', result.stderr)

    # If any exception happened
    if stderr:
        return re.sub(r'".+"', '"solution.py"', stderr)

    # If there's not displayed output
    if not stdout:
        return "No output"

    # If any of tests is failed
    for row in stdout.split('\n'):
        if "<FAILED::>" in row:
            return "Failed: {}.".format(re.search(r'<\w+::>(.+)', row).group(1))

    # If no one passed test
    if '<PASSED::>' not in stdout:
        return "No test is completed"


def check_password(password: str) -> bool:
    """Функция, проверяющая валидность пароля"""
    if len(password) >= 8 and \
            any(symbol in password for symbol in string.ascii_lowercase) and \
            any(sym in password for sym in string.digits) \
            and any(sym in password for sym in string.ascii_uppercase) \
            and any(sym in password for sym in string.punctuation):
        return True
    return False


@app.route("/kata_create", methods=["GET", "POST"])
def kata_create():
    """Обработчик создания задачи"""

    # Если пользователь не зарегистрирован
    if not current_user.is_authenticated:
        return render_template('unauthenticated.html')

    form = FormCreateTask()

    if request.method == "GET":
        if not current_user.is_authenticated:
            return render_template('is_not_authenticated.html')
        delete_past_catalogs()
        return render_template('create_task_.html', form=form, page={"title": "Create kata"}, current_user=current_user)

    elif request.method == "POST":
        db_kata_sess = db_session.create_session()
        error_msg_1 = None
        # Если имя задачи уже существует в базе данных
        if db_kata_sess.query(Kata).filter(Kata.title == form.title.data).first():
            error_msg_1 = "The task with the same name already exists"

        # Если в решении нет функции
        if not function_exists(form.completed_solution.data):
            error_msg_1 = "Function not in your solution"

        current_unique_folder_name = get_unique_foldername()

        error_msg_2 = check_file_output(current_unique_folder_name, FILE_SOLUTION,
                                        form.completed_solution.data, FILE_TEST, form.tests.data)

        if error_msg_2 or error_msg_1:
            return render_template('create_task_.html', page={"title": "Create kata"},
                                   form=form, error=(error_msg_1 or error_msg_2))

        kata = Kata()
        title = form.title.data
        kata.title = title
        kata.description = form.description.data
        kata.completed_solution = form.completed_solution.data
        kata.tests = form.tests.data
        kata.author_id = current_user.id
        kata.difficulty = -1
        kata.total_successful_solutions, kata.total_solutions = 0, 0
        db_kata_sess.add(kata)
        db_kata_sess.commit()

        delete_past_catalogs()

        return redirect(f'/')


@app.route('/')
def index():
    # Если пользователь не зарегистрирован
    if not current_user.is_authenticated:
        return render_template('unauthenticated.html')
    return render_template("index.html")


@app.route('/logout')
@login_required
def logout():
    """Выход из аккаунта"""
    delete_past_catalogs()  # Удаление предыдущих каталогов, созданных для создания или решения
    logout_user()
    return redirect('/')


@app.route('/register', methods=["GET", "POST"])
def register():
    """Обработчик регистрации"""
    form = FormRegister()
    if form.validate_on_submit():
        db_sess = db_session.create_session()

        error_message = None

        # Check if some data is already taken
        if db_sess.query(User).filter(User.nickname == form.nickname.data).first():
            error_message = "This username is already taken"

        if db_sess.query(User).filter(User.email == form.email.data).first():
            error_message = "This email is already taken"

        # Check if the input is valid
        if not all(symbol in possible_name_symbols for symbol in form.nickname.data):
            error_message = "Only letters, digits and '_' are allowed"

        if not check_email(form.email.data):
            error_message = "Email address is invalid"

        if not check_password(form.password.data):
            error_message = "Password must contain a-z, A-Z and 0-9 and at least 1 not alphabetic character"

        # Check match passwords
        if not form.password.data == form.repeated_password.data:
            error_message = "Passwords do not match"

        if isinstance(error_message, str):
            return render_template('register.html', form=form, current_user=current_user,
                                   error_msg=error_message)

        user = User()  # Создание нового экземпляра класса для добавления соответствующего пользователя в бд
        user.email = form.email.data
        user.nickname = form.nickname.data
        user.set_hashed_password(form.password.data)
        user.experience, user.solutions, user.created_katas = 0, 0, 0
        db_sess.add(user)
        db_sess.commit()

        return redirect('/')

    return render_template('register.html', form=form, current_user=current_user)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Обработчик логина"""
    form = FormLogin()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.nickname == form.nickname.data).first()

        error_message = None
        # If the user's nickname does not exist
        if not user:
            error_message = "Current user does not exist in the database"

        # If password do not match to real user's password field
        if user is not None:
            if not user.check_password(form.password.data):
                error_message = "Nick name or password is incorrect"

        if isinstance(error_message, str):  # Если ошибка произошла, обновлять веб-страницу с сообщением об ошибке
            return render_template("login.html", form=form, current_user=current_user, error_msg=error_message)

        login_user(user, remember=True)

        return redirect('/')

    return render_template('login.html', current_user=current_user, form=form)


@app.route('/katas_list/<string:difficult>')
def katas_list(difficult: str):
    """Функция, отвечающая за обработку страницы-списка всех задач"""

    # Если пользователь не зарегистрирован
    if not current_user.is_authenticated:
        return render_template('unauthenticated.html')

    db_session_ = db_session.create_session()
    list_of_katas = [{"ID": kata.id,
                      'title': kata.title,
                      "total": kata.total_solutions,
                      "total_success": kata.total_successful_solutions,
                      "creator": db_session_.query(User).filter(User.id == kata.author_id).first().nickname,
                      "diff": kata.difficulty,
                      'success_percentage': f'{(kata.total_successful_solutions / kata.total_solutions) * 100:.2f}'
                      if kata.total_solutions else 0}
                     for kata in db_session_.query(Kata).all()]

    return render_template('list_of_katas.html', difficult=difficult, list_of_kata=list_of_katas)


@app.route("/kata/<int:ID>", methods=['GET', 'POST'])
def show_kata(ID: int):
    """Функция, отвечающая за обработку страницы решения задачи"""

    # Если пользователь не зарегистрирован
    if not current_user.is_authenticated:
        return render_template('unauthenticated.html')

    form = SolveKata()

    db_sesss = db_session.create_session()
    kata = db_sesss.query(Kata).filter(Kata.id == ID).first()
    user = db_sesss.query(User).filter(User.id == kata.author_id).first()

    if request.method == "GET":
        delete_past_catalogs()
        return render_template("solve_kata.html", page={'title': 'Solve kata'},
                               form=form, kata={"title": kata.title, "difficult": kata.difficulty,
                                                "tests": kata.tests, "instruction": kata.description,
                                                "success": kata.total_successful_solutions,
                                                "total": kata.total_solutions,
                                                'author': user.nickname})

    if request.method == "POST":
        kata.total_solutions = kata.total_solutions + 1
        kata.difficulty = math.ceil((1 - (kata.total_successful_solutions / kata.total_solutions)) * 10)

        current_unique_folder_name = get_unique_foldername()

        error_msg = check_file_output(current_unique_folder_name, f"solution.py",
                                      form.solution.data, f"tests.py", kata.tests)

        if error_msg:
            db_sesss.commit()
            return render_template("solve_kata.html", error=error_msg, form=form, page={'title': 'Solve kata'},
                                   kata={"title": kata.title, "difficult": kata.difficulty,
                                         "tests": kata.tests, "instruction": kata.description,
                                         "author": user.nickname, "total": kata.total_solutions})

        else:
            user.experience = int(user.experience) + 1
            kata.total_successful_solutions = kata.total_successful_solutions + 1
            kata.difficulty = math.ceil((1 - (kata.total_successful_solutions / kata.total_solutions)) * 10)
            db_sesss.commit()

            delete_past_catalogs()

        return redirect("/katas_list/all")


if __name__ == '__main__':
    db_session.global_init(f"db_folder/data.db")
    app.run('127.0.0.1', port=8080)
