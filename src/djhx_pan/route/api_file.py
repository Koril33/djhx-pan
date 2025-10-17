import logging
import os
from datetime import datetime

from flask import Blueprint, request, send_from_directory
from flask_jwt_extended import (
    jwt_required
)

from .file import ICON_TYPES, _row_to_dict, UPLOAD_FOLDER, PREVIEW_TYPES, delete_entry
from ..config.app_config import AppConfig
from ..db import DB
from ..util import JsonResult, safe_secure_filename

app_logger = logging.getLogger(AppConfig.PROJECT_NAME + "." + __name__)

api_file_bp = Blueprint('api_file', __name__, url_prefix='/api/file')


@api_file_bp.route('/', methods=['GET'])
@jwt_required()
def api_file_page():
    parent_id = request.args.get('parent_id')
    if parent_id:
        # 取指定父目录下的条目
        rows = DB.query("SELECT * FROM t_file WHERE parent_id=?", (parent_id,))
    else:
        rows = DB.query("SELECT * FROM t_file WHERE parent_id IS NULL")

    # 保证 rows 为 list of dict
    rows = [_row_to_dict(r) for r in rows] if rows else []

    for r in rows:
        if r['is_dir']:
            r['icon_class'] = 'folder'
        else:
            filetype = (r.get('filetype') or '').lower()
            r['icon_class'] = ICON_TYPES.get(filetype, 'file')

    rows.sort(
        key=lambda r: (
            not r['is_dir'],
            -datetime.fromisoformat(r['create_datetime']).timestamp() if r['create_datetime'] else 0
        )
    )
    return JsonResult.successful(data=rows)


@api_file_bp.route('/upload', methods=['POST'])
@jwt_required()
def api_upload_file():
    # 支持传统表单上传（file input）和 fetch 上传（multipart）
    if 'file' not in request.files:
        return JsonResult.failed("请选择上传的文件")

    f = request.files['file']
    if f.filename == '':
        return JsonResult.failed("文件名不能为空")

    filename = safe_secure_filename(f.filename)
    if not filename:
        return JsonResult.failed("文件名不能为空")

    parent_id = request.form.get('parent_id') or None
    # 保存到 uploads 目录并避免同名覆盖
    save_path = os.path.join(UPLOAD_FOLDER, filename)

    counter = 1
    original_name = filename
    name_root, ext = os.path.splitext(original_name)
    while os.path.exists(save_path):
        filename = f"{name_root}_{counter}{ext}"
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        counter += 1

    try:
        f.save(save_path)
    except Exception as e:
        app_logger.exception("保存上传文件失败: %s", e)
        return JsonResult.failed("文件上传失败")

    # 检查是否为文件
    if not os.path.isfile(save_path):
        # 清理异常目录（极端情况）
        if os.path.exists(save_path) and os.path.isdir(save_path):
            try:
                os.rmdir(save_path)
            except Exception:
                pass
        return JsonResult.failed("上传内容不是有效文件")

    filesize = os.path.getsize(save_path)
    _, ext = os.path.splitext(filename)
    filetype = ext.lstrip('.').lower() if ext else ''
    now = datetime.now().isoformat()

    preview_type = PREVIEW_TYPES.get(filetype)

    DB.execute(
        """
        INSERT INTO t_file (filename, filesize, filetype, preview_type, filepath, is_dir, parent_id, create_datetime, update_datetime)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (filename, filesize, filetype, preview_type, save_path, 0, parent_id, now, now)
    )
    return JsonResult.successful("上传文件成功")


@api_file_bp.route('/download/<int:file_id>', methods=['GET'])
@jwt_required()
def api_download_file(file_id):
    rows = DB.query("SELECT * FROM t_file WHERE id=?", (file_id,))
    if not rows:
        return JsonResult.failed("文件不存在")
    row = _row_to_dict(rows[0])

    filepath = row.get('filepath')
    if not filepath:
        return JsonResult.failed("无法下载：未找到文件路径")
    directory = os.path.dirname(filepath)
    filename = os.path.basename(filepath)
    return send_from_directory(directory, filename, as_attachment=True)


@api_file_bp.route('/delete/<int:file_id>', methods=['POST'])
@jwt_required()
def api_delete_file_route(file_id):
    rows = DB.query("SELECT * FROM t_file WHERE id=?", (file_id,))
    if not rows:
        return JsonResult.failed("文件不存在")
    try:
        delete_entry(file_id)
    except Exception as e:
        app_logger.exception("删除条目 %s 失败: %s", file_id, e)
        return JsonResult.failed("删除失败")

    return JsonResult.successful("删除成功")