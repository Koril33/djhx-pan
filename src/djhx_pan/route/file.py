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
    rows = DB.query("SELECT * FROM t_file WHERE parent_id IS NULL")
    return render_template('file.html', files=rows)


@file_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash("未选择文件")
        return redirect(url_for('file.file_page'))

    f = request.files['file']
    if f.filename == '':
        flash("文件名为空")
        return redirect(url_for('file.file_page'))

    # 使用 secure_filename 安全处理文件名
    filename = safe_secure_filename(f.filename)
    if not filename:
        flash("无效的文件名")
        return redirect(url_for('file.file_page'))

    save_path = os.path.join(UPLOAD_FOLDER, filename)

    # 防止文件名冲突（可选：添加时间戳或 UUID）
    counter = 1
    original_save_path = save_path
    while os.path.exists(save_path):
        name, ext = os.path.splitext(original_save_path)
        save_path = f"{name}_{counter}{ext}"
        counter += 1
        # 也需更新 filename 以保持一致性
        filename = os.path.basename(save_path)

    # 保存文件
    f.save(save_path)

    # 确保保存的是文件而非目录（防御性检查）
    if not os.path.isfile(save_path):
        # 如果保存后不是文件（比如上传的是目录，虽然一般不会发生），删除并报错
        if os.path.exists(save_path):
            os.rmdir(save_path)  # 注意：仅适用于空目录
        flash("上传内容不是有效文件")
        return redirect(url_for('file.file_page'))

    filesize = os.path.getsize(save_path)

    # 更健壮地获取文件扩展名（保留点，但数据库字段可能不需要点）
    _, ext = os.path.splitext(filename)
    filetype = ext.lstrip('.').lower() if ext else ''  # 转小写更规范

    now = datetime.datetime.now().isoformat()

    # is_dir 明确设为 0（因为上传的是文件），但逻辑清晰
    is_dir = 0  # 因为 f.save() 保存的是文件，不是目录

    DB.execute(
        """
        INSERT INTO t_file (filename, filesize, filetype, filepath, is_dir, create_datetime, update_datetime)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (filename, filesize, filetype, save_path, is_dir, now, now)
    )

    return redirect(url_for('file.file_page'))


@file_bp.route('/download/<int:file_id>', methods=['GET'])
def download_file(file_id):
    row = DB.query("SELECT * FROM t_file WHERE id=?", (file_id,))[0]
    if not row:
        return "文件不存在", 404

    directory = os.path.dirname(row['filepath'])
    filename = os.path.basename(row['filepath'])
    return send_from_directory(directory, filename, as_attachment=True)


@file_bp.route('/delete/<int:file_id>', methods=['POST'])
def delete_file(file_id):

    row = DB.query("SELECT * FROM t_file WHERE id=?", (file_id,))[0]
    if not row:
        return "文件不存在", 404

    if os.path.exists(row['filepath']):
        os.remove(row['filepath'])

    DB.execute("DELETE FROM t_file WHERE id=?", (file_id,))
    return redirect(url_for('file.file_page'))
