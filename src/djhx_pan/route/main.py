import datetime
import logging

from flask import Blueprint, render_template, session

from .file import ICON_TYPES, _row_to_dict
from ..config.app_config import AppConfig
from ..util import login_required
from ..db import DB

main_bp = Blueprint('main', __name__)
app_logger = logging.getLogger(AppConfig.PROJECT_NAME + "." + __name__)


@main_bp.route('/', methods=['GET', 'POST'])
def index():
    app_logger.debug(f'session user: {session.get("user")}')
    s_user = session.get("user")
    username = 'anonymous'
    if s_user:
        username = s_user.get('username')

    public_shares = DB.query("""
        SELECT
            t_share.id as share_id,
            t_file.id as file_id,
            *
        FROM t_share 
        JOIN t_file ON t_share.file_id = t_file.id
        WHERE password IS NULL AND (expires_at IS NULL OR expires_at > ?) AND t_file.is_dir = 0
    """, (datetime.datetime.now().isoformat(), ))

    public_shares = [_row_to_dict(r) for r in public_shares] if public_shares else []

    for f in public_shares:
        f['icon_class'] = 'folder' if f['is_dir'] else ICON_TYPES.get((f.get('filetype') or '').lower(), 'file')
    public_shares.sort(key=lambda r: (not r['is_dir'],
                              -datetime.datetime.fromisoformat(r['create_datetime']).timestamp() if r[
                                  'create_datetime'] else 0))

    return render_template('index.html', username=username, files=public_shares)


@main_bp.get('/dashboard')
@login_required
def dashboard():
    s_user = session.get("user")
    username = 'anonymous'
    if s_user:
        username = s_user.get('username')
    return render_template('dashboard.html', username=username)
