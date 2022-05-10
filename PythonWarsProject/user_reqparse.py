from data import db_session
from data.users import User

from flask_restful import reqparse


parser = reqparse.RequestParser()
parser.add_argument("nickname", type=str, required=True)
parser.add_argument("email", type=str, required=True)
parser.add_argument("pswrd", type=str, required=True)
