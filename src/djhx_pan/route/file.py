import datetime
import logging
import os

from flask import Blueprint, request, render_template, send_from_directory, redirect, url_for, flash

from ..config.app_config import AppConfig
from ..db import DB
from ..util import safe_secure_filename

app_logger = logging.getLogger(AppConfig.PROJECT_NAME + "." + __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

file_bp = Blueprint('file', __name__, url_prefix='/file')


@file_bp.route('/', methods=['GET'])
def file_page():
    parent_id = request.args.get('parent_id')
    if parent_id:
        rows = DB.query("SELECT * FROM t_file WHERE parent_id=?", (parent_id,))
    else:
        rows = DB.query("SELECT * FROM t_file WHERE parent_id IS NULL")

    parent = None
    if parent_id:
        parent_result = DB.query("SELECT * FROM t_file WHERE id=?", (parent_id,))
        parent = parent_result[0] if parent_result else None

    return render_template('file.html', files=rows, parent=parent)


@file_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash("未选择文件")
        return redirect(url_for('file.file_page'))

    f = request.files['file']
    if f.filename == '':
        flash("文件名为空")
        return redirect(url_for('file.file_page'))

    filename = safe_secure_filename(f.filename)
    if not filename:
        flash("无效的文件名")
        return redirect(url_for('file.file_page'))

    parent_id = request.form.get('parent_id') or None
    save_path = os.path.join(UPLOAD_FOLDER, filename)

    counter = 1
    original_save_path = save_path
    while os.path.exists(save_path):
        name, ext = os.path.splitext(original_save_path)
        save_path = f"{name}_{counter}{ext}"
        counter += 1
        filename = os.path.basename(save_path)

    f.save(save_path)

    if not os.path.isfile(save_path):
        if os.path.exists(save_path):
            os.rmdir(save_path)
        flash("上传内容不是有效文件")
        return redirect(url_for('file.file_page'))

    filesize = os.path.getsize(save_path)
    _, ext = os.path.splitext(filename)
    filetype = ext.lstrip('.').lower() if ext else ''
    now = datetime.datetime.now().isoformat()

    DB.execute(
        """
        INSERT INTO t_file (filename, filesize, filetype, filepath, is_dir, parent_id, create_datetime, update_datetime)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (filename, filesize, filetype, save_path, 0, parent_id, now, now)
    )

    return redirect(url_for('file.file_page', parent_id=parent_id))


@file_bp.route('/create-folder', methods=['POST'])
def create_folder():
    name = request.form.get('folder_name')
    parent_id = request.form.get('parent_id')
    now = datetime.datetime.now().isoformat()

    if not name:
        flash("文件夹名称不能为空")
        return redirect(url_for('file.file_page', parent_id=parent_id))

    DB.execute("""
        INSERT INTO t_file (filename, is_dir, parent_id, create_datetime, update_datetime)
        VALUES (?, ?, ?, ?, ?)
    """, (name, 1, parent_id if parent_id else None, now, now))

    return redirect(url_for('file.file_page', parent_id=parent_id))


@file_bp.route('/download/<int:file_id>', methods=['GET'])
def download_file(file_id):
    rows = DB.query("SELECT * FROM t_file WHERE id=?", (file_id,))
    if not rows:
        return "文件不存在", 404
    row = rows[0]

    directory = os.path.dirname(row['filepath'])
    filename = os.path.basename(row['filepath'])
    return send_from_directory(directory, filename, as_attachment=True)


@file_bp.route('/delete/<int:file_id>', methods=['POST'])
def delete_file(file_id):
    rows = DB.query("SELECT * FROM t_file WHERE id=?", (file_id,))
    if not rows:
        return "文件不存在", 404
    row = rows[0]

    if row['is_dir']:
        # 删除文件夹（递归）
        children = DB.query("SELECT id FROM t_file WHERE parent_id=?", (file_id,))
        for c in children:
            delete_file(c['id'])
    else:
        if os.path.exists(row['filepath']):
            os.remove(row['filepath'])

    DB.execute("DELETE FROM t_file WHERE id=?", (file_id,))
    return redirect(url_for('file.file_page', parent_id=row.get('parent_id')))
