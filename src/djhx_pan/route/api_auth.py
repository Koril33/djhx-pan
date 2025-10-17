import logging
import random
import string
import time
from datetime import timedelta

from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity
)

from ..config.app_config import AppConfig
from ..db import DB
from ..util import PasswordUtil, send_email_verify_code, JsonResult

app_logger = logging.getLogger(AppConfig.PROJECT_NAME + "." + __name__)

api_auth_bp = Blueprint('api_auth', __name__, url_prefix='/api/auth')

# 简单内存验证码缓存，可换 Redis
email_code_cache = {}

JWT_EXPIRATION_DELTA = timedelta(minutes=60)

@api_auth_bp.route('/login', methods=['POST'])
def api_login():
    data = request.get_json()
    login_type = data.get('login_type', 'username')

    if login_type == 'username':
        username = data.get('username')
        password = data.get('password')
        db_user = DB.query("SELECT username, password, salt FROM t_user WHERE username = ?", (username,))
        if not db_user:
            return JsonResult.failed("用户不存在")
        user = db_user[0]
        if not PasswordUtil.verify_password(password, user['password'], user['salt']):
            return JsonResult.failed("密码错误")
        token = create_access_token(identity=username, expires_delta=JWT_EXPIRATION_DELTA)
        token_data = {'access_token': token}
        return JsonResult.successful("登陆成功", token_data)

    elif login_type == 'email':
        email = data.get('email')
        code = data.get('code')
        db_user = DB.query("SELECT username FROM t_user WHERE email = ?", (email,))
        if not db_user:
            return JsonResult.failed("邮箱未注册")
        stored = email_code_cache.get(email)
        if not stored:
            return JsonResult.failed("请先获取验证码")
        if time.time() - stored['time'] > 300:
            return JsonResult.failed("验证码已过期")
        if stored['code'] != code:
            return JsonResult.failed("验证码错误")
        username = db_user[0]['username']
        token = create_access_token(identity=username, expires_delta=JWT_EXPIRATION_DELTA)
        email_code_cache.pop(email, None)
        token_data = {'access_token': token, 'username': username}
        return JsonResult.successful("登陆成功", token_data)

    return JsonResult.failed("未知登录类型")


@api_auth_bp.route('/register', methods=['POST'])
def api_register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    password_confirm = data.get('password_confirm')

    if password != password_confirm:
        return JsonResult.failed("两次密码不一致")

    existing_user = DB.query("SELECT username FROM t_user WHERE username = ?", (username,))
    if existing_user:
        return JsonResult.failed("用户名已存在")

    salt = PasswordUtil.generate_salt()
    password_hash = PasswordUtil.hash_password(password, salt)
    DB.execute(
        "INSERT INTO t_user (username, password, salt, nickname) VALUES (?, ?, ?, ?)",
        (username, password_hash, salt, username)
    )
    return JsonResult.successful("注册成功")


@api_auth_bp.route('/send_code', methods=['POST'])
def api_send_code():
    data = request.get_json()
    email = data.get('email')

    db_user = DB.query("SELECT id FROM t_user WHERE email = ?", (email,))
    if not db_user:
        return JsonResult.failed("邮箱未注册")

    code = ''.join(random.choices(string.digits, k=6))
    email_code_cache[email] = {'code': code, 'time': time.time()}

    try:
        send_email_verify_code(email, code)
        app_logger.info(f"Send code {code} to {email}")
        return JsonResult.successful("验证码已发送")
    except Exception as e:
        app_logger.exception(f'邮件发送失败: {e}')
        return JsonResult.failed("发送失败")


@api_auth_bp.route('/me', methods=['GET'])
@jwt_required()
def api_me():
    username = get_jwt_identity()
    db_user = DB.query("SELECT username, nickname, email FROM t_user WHERE username = ?", (username,))
    if not db_user:
        return JsonResult.failed("用户不存在")
    # return jsonify({'success': True, 'user': db_user[0]})
    data = {
        'user': db_user[0]
    }
    return JsonResult.successful("ok", data)


@api_auth_bp.route('/logout', methods=['POST'])
@jwt_required(optional=True)
def api_logout():
    # 无状态，客户端直接丢弃 token 即可
    return JsonResult.successful("已登出")
