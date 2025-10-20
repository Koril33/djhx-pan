import random
import string
import time
from dataclasses import dataclass
from datetime import timedelta

from flask_jwt_extended import create_access_token, create_refresh_token

from ..config.log_config import project_logger
from ..exception import ClientError
from ..repository import user_repo
from ..repository.user_repo import get_user_by_email
from ..util import PasswordUtil, send_email_verify_code
from ..model import User

app_logger = project_logger()

JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=60)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)

# 简单内存验证码缓存，可换 Redis
email_code_cache = {}

@dataclass
class TokenData:
    access_token: str
    refresh_token: str = None
    token_type: str = "Bearer"

    def to_dict(self) -> dict:
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "token_type": self.token_type
        }

def login_by_username(username: str, password: str) -> TokenData | None:
    user = user_repo.get_user_by_username(username)
    if not user:
        raise ClientError(f'用户 {username} 不存在')

    if not PasswordUtil.verify_password(password, user.password, user.salt):
        raise ClientError(f'用户名或密码错误')

    access_token = create_access_token(identity=user.username, expires_delta=JWT_ACCESS_TOKEN_EXPIRES)
    refresh_token = create_refresh_token(identity=user.username, expires_delta=JWT_REFRESH_TOKEN_EXPIRES)
    return TokenData(access_token=access_token, refresh_token=refresh_token)


def login_by_email(email: str, email_code: str) -> TokenData | None:
    user = get_user_by_email(email)
    if not user:
        raise ClientError(f'邮箱 {email} 未注册')
    stored = email_code_cache.get(email)
    if not stored:
        raise ClientError("请先获取邮箱验证码")
    if time.time() - stored['time'] > 300:
        raise ClientError("验证码已过期")
    if stored['code'] != email_code:
        raise ClientError("验证码错误")
    access_token = create_access_token(identity=user.username, expires_delta=JWT_ACCESS_TOKEN_EXPIRES)
    refresh_token = create_refresh_token(identity=user.username, expires_delta=JWT_REFRESH_TOKEN_EXPIRES)
    email_code_cache.pop(email, None)
    return TokenData(access_token=access_token, refresh_token=refresh_token)


def user_register(username: str, password: str, password_confirm: str, email: str, phone: str,) -> User | None:
    if password != password_confirm:
        raise ClientError('两次密码不一致')

    if user_repo.get_user_by_username(username):
        raise ClientError(f'用户名 {username} 已存在')

    if email and user_repo.get_user_by_email(email):
        raise ClientError(f'邮箱 {email} 已被注册')

    if phone and user_repo.get_user_by_phone(phone):
        raise ClientError(f'手机号 {phone} 已被注册')

    salt = PasswordUtil.generate_salt()
    password_hash = PasswordUtil.hash_password(password, salt)
    new_user = user_repo.add_user(username, username, password_hash, salt, email, phone)
    return new_user


def send_email_code(email: str) -> None:

    user = user_repo.get_user_by_email(email)
    if not user:
        raise ClientError(f'邮箱 {email} 未注册')

    code = ''.join(random.choices(string.digits, k=6))
    email_code_cache[email] = {'code': code, 'time': time.time()}

    try:
        send_email_verify_code(email, code)
    except Exception as e:
        raise e


def refresh_token(username: str) -> TokenData | None:
    user = user_repo.get_user_by_username(username)
    if not user:
        raise ClientError(f'用户 {username} 不存在')
    access_token = create_access_token(identity=user.username, expires_delta=JWT_ACCESS_TOKEN_EXPIRES)
    return TokenData(access_token=access_token)