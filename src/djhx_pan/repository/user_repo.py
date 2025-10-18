from ..extension import db
from ..model import User


def get_user_by_email(email: str) -> User:
    return User.query.filter_by(email=email).first()


def get_user_by_username(username: str) -> User:
    return User.query.filter_by(username=username).first()


def get_user_by_phone(phone):
    return User.query.filter_by(phone=phone).first()


def add_user(username: str, nickname: str, password: str, salt: str, email: str, phone: str, ):
    user = User(username=username, nickname=nickname, password=password, salt=salt, email=email, phone=phone)
    db.session.add(user)
    db.session.commit()
    return user
