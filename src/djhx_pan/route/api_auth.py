import logging

from flask import Blueprint, request
from flask_jwt_extended import (
    jwt_required, get_jwt_identity
)

from ..config.app_config import AppConfig
from ..exception import ClientError, ServerError
from ..service import user_service
from ..util import JsonResult
from ..repository import user_repo

app_logger = logging.getLogger(AppConfig.PROJECT_NAME + "." + __name__)

api_auth_bp = Blueprint('api_auth', __name__, url_prefix='/api/auth')

@api_auth_bp.route('/login', methods=['POST'])
def api_login():
    data = request.get_json()
    login_type = data.get('login_type', 'username')

    if login_type == 'username':
        username = data.get('username')
        password = data.get('password')
        token_data = user_service.login_by_username(username, password)
        if not token_data:
            raise ServerError('无法生成 Token Data')
        else:
            return JsonResult.successful('用户名密码登录成功', token_data)
    elif login_type == 'email':
        email = data.get('email')
        code = data.get('code')
        token_data = user_service.login_by_email(email, code)
        if not token_data:
            raise ServerError('无法生成 Token Data')
        return JsonResult.successful('邮箱登陆成功', token_data)

    raise ClientError(f'未知的登录类型: {login_type}')


@api_auth_bp.route('/register', methods=['POST'])
def api_register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    password_confirm = data.get('password_confirm')
    phone = data.get('phone')
    email = data.get('email')

    new_user = user_service.user_register(username, password, password_confirm, email, phone)
    if not new_user:
        raise ServerError(f'用户注册失败')
    return JsonResult.successful(f'用户 {new_user.username} 注册成功')


@api_auth_bp.route('/send_code', methods=['POST'])
def api_send_code():
    data = request.get_json()
    email = data.get('email')
    user_service.send_email_code(email)
    return JsonResult.successful(f'邮箱验证码已发送')


@api_auth_bp.route('/me', methods=['GET'])
@jwt_required()
def api_me():
    username = get_jwt_identity()
    user = user_repo.get_user_by_username(username)
    if not user:
        raise ClientError(f'用户不存在')
    user_info = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'phone': user.phone,
    }
    return JsonResult.successful("ok", user_info)


@api_auth_bp.route('/logout', methods=['POST'])
@jwt_required(optional=True)
def api_logout():
    # 无状态，客户端直接丢弃 token 即可
    return JsonResult.successful("已登出")
