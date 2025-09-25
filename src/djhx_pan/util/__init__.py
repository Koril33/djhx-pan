import base64
import hashlib
import hmac
import os
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from functools import wraps

from flask import jsonify, session, redirect, url_for, request


class JsonResult:
    def __init__(self, success: bool, message: str, data: object):
        self.success = success
        self.message = message
        self.data = data

    def res(self):
        return jsonify({
            'success': self.success,
            'message': self.message,
            'data': self.data
        })

    @staticmethod
    def successful(message: str = 'ok', data: object = None):
        return JsonResult(True, message, data).res()

    @staticmethod
    def failed(message: str = 'fail', data: object = None):
        return JsonResult(False, message, data).res()


class PasswordUtil:

    ITERATIONS = 65536
    KEY_LENGTH = 32  # 256 位 / 8
    ALGORITHM = 'sha256'

    @staticmethod
    def generate_salt(length: int = 16) -> str:
        """生成随机 Salt（Base64 编码）"""
        salt_bytes = os.urandom(length)
        return base64.b64encode(salt_bytes).decode('utf-8')

    @staticmethod
    def hash_password(password: str, salt: str) -> str:
        """生成密码哈希（PBKDF2 + Salt + Base64 编码）"""
        salt_bytes = base64.b64decode(salt)
        dk = hashlib.pbkdf2_hmac(
            PasswordUtil.ALGORITHM,
            password.encode('utf-8'),
            salt_bytes,
            PasswordUtil.ITERATIONS,
            dklen=PasswordUtil.KEY_LENGTH
        )
        return base64.b64encode(dk).decode('utf-8')

    @staticmethod
    def verify_password(input_password: str, stored_hash: str, stored_salt: str) -> bool:
        """验证密码"""
        new_hash = PasswordUtil.hash_password(input_password, stored_salt)
        return hmac.compare_digest(new_hash, stored_hash)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            # 记录原始请求路径，登录后跳转回来
            session['next_url'] = request.url
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)

    return decorated_function


def send_email_verify_code(email, code):
    smtp_server = 'smtp.163.com'
    smtp_port = 465

    # 发件人邮箱地址和授权码
    sender_email = 'dingjinghui33@163.com'
    sender_password = 'SBAFQUEJINKBHYGS'

    # 收件人邮箱地址
    recipient_email = [email]

    message = MIMEText(f'djhx-pan email verify code: {code}', 'plain', 'utf-8')
    message['From'] = sender_email
    message['To'] = ",".join(recipient_email)
    message['Subject'] = Header('djhx-pan email verify code', 'utf-8')

    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, message.as_string())