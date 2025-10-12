import logging
import random
import string
import time

from flask import Blueprint, request, session, redirect, render_template, url_for, jsonify

from ..config.app_config import AppConfig
from ..db import DB
from ..util import PasswordUtil, send_email_verify_code, login_required

app_logger = logging.getLogger(AppConfig.PROJECT_NAME + "." + __name__)

user_bp = Blueprint('user', __name__)


@user_bp.route('/user/page', methods=['GET', 'POST'])
@login_required
def page():
    return render_template('user.html')