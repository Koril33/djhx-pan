import logging
import random
import string
import time

from flask import Blueprint, request, session, redirect, render_template, url_for, jsonify

from ..config.app_config import AppConfig
from ..db import DB
from ..util import PasswordUtil, send_email_verify_code

app_logger = logging.getLogger(AppConfig.PROJECT_NAME + "." + __name__)

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    username = None
    email = None
    login_type = 'username'
    error = None

    if request.method == 'POST':
        login_type = request.form.get('login_type', 'username')

        if login_type == 'username':
            # 用户名密码登录
            username = request.form.get('username')
            password = request.form.get('password')
            db_user = DB.query(
                "SELECT username, password, salt FROM t_user WHERE username = ?",
                (username,)
            )
            if db_user:
                db_user = db_user[0]
                if PasswordUtil.verify_password(password, db_user.get('password'), db_user.get('salt')):
                    session.permanent = True
                    session['user'] = {'username': username}
                    next_url = session.pop('next_url', None) or url_for('main.index')
                    return redirect(next_url)
                else:
                    error = '密码错误'
            else:
                error = f'用户 {username} 不存在'

        elif login_type == 'email':
            # 邮箱验证码登录
            email = request.form.get('email')
            code = request.form.get('code')
            db_user = DB.query("SELECT username FROM t_user WHERE email = ?", (email,))
            if not db_user:
                error = f'邮箱 {email} 未注册'
            else:
                stored = session.get('email_code')
                if stored and stored['email'] == email:
                    if time.time() - stored['time'] > 300:  # 5分钟有效
                        error = '验证码已过期'
                    elif stored['code'] != code:
                        error = '验证码错误'
                    else:
                        # 登录成功
                        session.permanent = True
                        session['user'] = {'username': db_user[0]['username']}
                        session.pop('email_code', None)  # 删除验证码
                        next_url = session.pop('next_url', None) or url_for('main.index')
                        return redirect(next_url)
                else:
                    error = '请先获取验证码'

    return render_template('login.html', error=error, username=username, email=email, login_type=login_type)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')

        if password != password_confirm:
            return render_template('register.html', error='两次密码不一致')

        # 检查用户是否已存在
        existing_user = DB.query(
            """
            SELECT username
            FROM t_user
            WHERE username = ?;
            """,
            (username,)
        )

        if existing_user:
            error = f'用户名 {username} 已存在'
        else:
            # 生成 salt 和 hash
            salt = PasswordUtil.generate_salt()
            password_hash = PasswordUtil.hash_password(password, salt)

            # 存储到数据库
            DB.execute(
                """
                INSERT INTO t_user
                    (username, password, salt, nickname)
                VALUES (?, ?, ?, ?);
                """,
                (username, password_hash, salt, username)
            )

            # 注册成功后跳转到登录页
            return redirect(url_for('auth.login'))

    return render_template('register.html', error=error)


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))


@auth_bp.route('/send_code', methods=['POST'])
def send_code():
    data = request.get_json()
    email = data.get('email')

    # 检查邮箱是否存在
    db_user = DB.query("SELECT id FROM t_user WHERE email = ?", (email,))
    if not db_user:
        return jsonify({'success': False, 'message': '该邮箱未注册'})

    # 生成6位验证码
    code = ''.join(random.choices(string.digits, k=6))
    session['email_code'] = {'email': email, 'code': code, 'time': time.time()}

    app_logger.info(f"Send code {code} to {email}")
    try:
        send_email_verify_code(email, code)
    except Exception as e:
        app_logger.exception(f'邮件 {email} 验证码发送失败: {e}')
    else:
        app_logger.info(f'邮件 {email} 验证码发送成功')

    return jsonify({'success': True, 'message': '验证码已发送，请查收邮件'})
