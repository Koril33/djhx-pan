import datetime
import logging
import os
from typing import Optional, Dict, Any, List

from flask import Blueprint, request, render_template, send_from_directory, redirect, url_for, flash

from ..config.app_config import AppConfig
from ..db import DB
from ..util import safe_secure_filename

app_logger = logging.getLogger(AppConfig.PROJECT_NAME + "." + __name__)

# 上传目录（项目内相对路径）
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

file_bp = Blueprint('file', __name__, url_prefix='/file')

ICON_TYPES = {

    ## 特殊处理
    "md": "markdown",
    "json": "json",
    "py": "python",
    "java": "java",

    ## 大类
    # 文档类
    "pdf": "pdf",
    "txt": "text", "rtf": "text",
    "xml": "text",
    "yml": "text", "toml": "text",

    # Office 文档
    "doc": "word", "docx": "word", "odt": "word",
    "xls": "spreadsheet", "xlsx": "spreadsheet", "ods": "spreadsheet",
    "ppt": "presentation", "pptx": "presentation", "odp": "presentation",

    # 图片类
    "jpg": "image", "jpeg": "image", "png": "image", "gif": "image",
    "webp": "image", "bmp": "image", "tif": "image", "tiff": "image",
    "svg": "image", "ico": "image", "heic": "image", "avif": "image",
    "psd": "image", "ai": "image", "eps": "image",

    # 音频类
    "mp3": "audio", "wav": "audio", "flac": "audio", "aac": "audio",
    "ogg": "audio", "m4a": "audio", "wma": "audio", "aiff": "audio",
    "mid": "audio", "midi": "audio", "amr": "audio",

    # 视频类
    "mp4": "video", "avi": "video", "mkv": "video", "mov": "video",
    "flv": "video", "wmv": "video", "webm": "video", "mpeg": "video", "mpg": "video",
    "m4v": "video", "m3u8": "video", "3gp": "video",

    # 压缩包类
    "zip": "archive", "rar": "archive", "7z": "archive",
    "tar": "archive", "gz": "archive", "bz2": "archive", "xz": "archive",
    "tgz": "archive", "tar.gz": "archive", "iso": "archive", "dmg": "archive",

    # 代码 / 脚本类
    "pyc": "code", "pyo": "code",
    "js": "code", "ts": "code", "jsx": "code", "tsx": "code",
    "html": "code", "htm": "code", "css": "code",
    "class": "code", "jar": "code",
    "c": "code", "cpp": "code", "h": "code", "hpp": "code", "cs": "code",
    "go": "code", "rs": "code", "php": "code", "rb": "code",
    "swift": "code", "kt": "code", "kts": "code", "dart": "code",
    "json5": "code", "vue": "code", "jsp": "code", "asp": "code", "aspx": "code",
    "sql": "code", "db": "code", "sqlite": "code",
    "bat": "code", "cmd": "code", "sh": "code", "bash": "code", "zsh": "code",

    # 系统类
    "exe": "binary", "msi": "binary", "bin": "binary", "dll": "binary",
    "so": "binary", "dylib": "binary", "sys": "binary",
    "apk": "binary", "ipa": "binary", "app": "binary", "run": "binary",
    "pkg": "binary", "img": "binary", "vmdk": "binary", "vdi": "binary",
    "ovf": "binary", "ova": "binary",

    # 设计 / 3D / CAD
    "dwg": "design", "dxf": "design", "blend": "design",
    "obj": "design", "fbx": "design", "stl": "design",
    "3ds": "design", "gltf": "design", "glb": "design",
    "indd": "design", "xd": "design", "sketch": "design",

    # 字体类
    "ttf": "font", "otf": "font", "woff": "font", "woff2": "font", "eot": "font",

    # 数据 / 备份
    "bak": "backup", "old": "backup", "tmp": "backup", "swp": "backup",

    # 其他常见文件
    "torrent": "torrent",
    "url": "link", "lnk": "link",
    "eml": "mail", "msg": "mail",
    "ics": "calendar",
    "crt": "certificate", "pem": "certificate", "key": "certificate",
    "csv": "spreadsheet", "tsv": "spreadsheet",

    # 电子书类
    "epub": "ebook", "mobi": "ebook", "azw3": "ebook", "cbz": "ebook", "cbr": "ebook",

    # 日志 / 监控类
    "log": "text", "out": "text", "err": "text",

    # 配置类
    "env": "config", "properties": "config", "ini": "config",
    "cfg": "config", "conf": "config", "yaml": "config",
}


def _row_to_dict(row) -> Dict[str, Any]:
    """
    如果 DB.query 返回的是 dict-like 或 sqlite Row，这里保证是 dict
    """
    try:
        return dict(row)
    except Exception:
        return row


def build_breadcrumbs(start_parent_id: Optional[int]) -> List[Dict[str, Any]]:
    """
    从当前 parent_id 向上查父节点，生成面包屑（根不包含 None）
    返回列表，顺序是从根向下到当前（root...current）
    """
    crumbs: List[Dict[str, Any]] = []
    pid = start_parent_id
    safety = 0
    while pid:
        safety += 1
        if safety > 100:
            break
        rows = DB.query("SELECT * FROM t_file WHERE id=?", (pid,))
        if not rows:
            break
        row = _row_to_dict(rows[0])
        crumbs.append({'id': row.get('id'), 'filename': row.get('filename')})
        pid = row.get('parent_id')
    crumbs.reverse()
    return crumbs


def delete_entry(entry_id: int):
    """
    递归删除一个 t_file 条目：
    - 如果是文件，删除物理文件（如果存在）
    - 如果是目录，递归删除子条目
    - 最后删除数据库记录本身
    """
    rows = DB.query("SELECT * FROM t_file WHERE id=?", (entry_id,))
    if not rows:
        return
    row = _row_to_dict(rows[0])

    if row.get('is_dir'):
        # 先删除子节点
        children = DB.query("SELECT id FROM t_file WHERE parent_id=?", (entry_id,))
        for c in children:
            # c 可能是 Row-like
            cid = c.get('id') if isinstance(c, dict) else c[0] if len(c) else None
            if cid:
                delete_entry(cid)
    else:
        filepath = row.get('filepath')
        try:
            if filepath and os.path.exists(filepath) and os.path.isfile(filepath):
                os.remove(filepath)
        except Exception as e:
            app_logger.warning("删除文件 %s 时出错: %s", filepath, e)

    # 删除数据库记录
    DB.execute("DELETE FROM t_file WHERE id=?", (entry_id,))


@file_bp.app_template_filter('format_file_size')
def format_file_size(size_in_bytes, decimals=2):
    """
    自动将字节 (Bytes) 转换为最合适的单位 (B, KB, MB, GB, TB)。

    Args:
        size_in_bytes (int): 要转换的字节数。
        decimals (int): 要保留的小数位数，默认为 2。

    Returns:
        str: 格式化后的文件大小字符串，例如 "1.50 MB"。
    """
    # 1. 处理无效或零值
    if size_in_bytes is None or size_in_bytes == 0:
        return '0 B'

    # 2. 定义基数和单位列表
    k = 1024
    # 使用 Python 的内置的 float() 来确保输入是数字
    bytes_float = float(size_in_bytes)

    sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']

    # 3. 计算对数和索引
    # 使用 math.log 确定最合适的单位索引
    import math
    i = math.floor(math.log(bytes_float, k))

    # 4. 确保小数位数的有效性
    decimals = max(0, decimals)

    # 5. 进行计算和格式化
    # size_in_bytes / (k ** i) 计算出转换后的数值
    # 使用 f-string 进行精确格式化
    value = bytes_float / (k ** i)
    format_string = f"{{:.{decimals}f}}"

    return f"{format_string.format(value)} {sizes[i]}"


@file_bp.route('/', methods=['GET'])
def file_page():
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
            -datetime.datetime.fromisoformat(r['create_datetime']).timestamp() if r['create_datetime'] else 0
        )
    )

    parent = None
    if parent_id:
        parent_result = DB.query("SELECT * FROM t_file WHERE id=?", (parent_id,))
        parent = _row_to_dict(parent_result[0]) if parent_result else None

    # 生成面包屑，从根到当前
    breadcrumbs = build_breadcrumbs(parent.get('id') if parent else None)

    return render_template('file.html', files=rows, parent=parent, breadcrumbs=breadcrumbs)


@file_bp.route('/upload', methods=['POST'])
def upload_file():
    # 支持传统表单上传（file input）和 fetch 上传（multipart）
    if 'file' not in request.files:
        flash("未选择文件")
        # 保持 parent_id 如果有的话
        return redirect(url_for('file.file_page', parent_id=request.form.get('parent_id') or None))

    f = request.files['file']
    if f.filename == '':
        flash("文件名为空")
        return redirect(url_for('file.file_page', parent_id=request.form.get('parent_id') or None))

    filename = safe_secure_filename(f.filename)
    if not filename:
        flash("无效的文件名")
        return redirect(url_for('file.file_page', parent_id=request.form.get('parent_id') or None))

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
        flash("保存文件失败")
        return redirect(url_for('file.file_page', parent_id=parent_id))

    # 检查是否为文件
    if not os.path.isfile(save_path):
        # 清理异常目录（极端情况）
        if os.path.exists(save_path) and os.path.isdir(save_path):
            try:
                os.rmdir(save_path)
            except Exception:
                pass
        flash("上传内容不是有效文件")
        return redirect(url_for('file.file_page', parent_id=parent_id))

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

    # 上传后若是 fetch 提交通常会返回 200；这里统一重定向到目录页
    return redirect(url_for('file.file_page', parent_id=parent_id))


@file_bp.route('/create-folder', methods=['POST'])
def create_folder():
    name = request.form.get('folder_name')
    parent_id = request.form.get('parent_id')
    now = datetime.datetime.now().isoformat()

    if not name:
        flash("文件夹名称不能为空")
        return redirect(url_for('file.file_page', parent_id=parent_id))

    # 插入目录记录（filepath 为 NULL）
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
    row = _row_to_dict(rows[0])

    filepath = row.get('filepath')
    if not filepath:
        return "无法下载：未找到文件路径", 404
    directory = os.path.dirname(filepath)
    filename = os.path.basename(filepath)
    # send_from_directory 将处理文件名编码等
    return send_from_directory(directory, filename, as_attachment=True)


@file_bp.route('/delete/<int:file_id>', methods=['POST'])
def delete_file_route(file_id):
    rows = DB.query("SELECT * FROM t_file WHERE id=?", (file_id,))
    if not rows:
        return "文件不存在", 404
    row = _row_to_dict(rows[0])

    # 先删除物理文件/子文件（由 helper 完成）
    try:
        delete_entry(file_id)
    except Exception as e:
        app_logger.exception("删除条目 %s 失败: %s", file_id, e)
        flash("删除失败")
        return redirect(url_for('file.file_page', parent_id=row.get('parent_id')))

    return redirect(url_for('file.file_page', parent_id=row.get('parent_id')))


@file_bp.route('/delete-multiple', methods=['POST'])
def delete_multiple():
    """
    处理批量删除请求。前端传来 selected_ids 字符串（逗号分隔）。
    """
    selected = request.form.get('selected_ids') or ''
    if not selected:
        flash("未选择要删除的项")
        return redirect(url_for('file.file_page'))

    try:
        parts = [p.strip() for p in selected.split(',') if p.strip()]
        ids = [int(p) for p in parts]
    except Exception:
        flash("传入的 id 格式错误")
        return redirect(url_for('file.file_page'))

    # 为了返回到合适的目录，尝试读取第一个 id 的 parent_id
    parent_id = None
    first_row = DB.query("SELECT parent_id FROM t_file WHERE id=?", (ids[0],)) if ids else None
    if first_row:
        try:
            parent_id = first_row[0].get('parent_id') if isinstance(first_row[0], dict) else first_row[0][0]
        except Exception:
            parent_id = None

    # 逐个删除
    for _id in ids:
        try:
            delete_entry(_id)
        except Exception as e:
            app_logger.exception("批量删除时 %s 失败: %s", _id, e)
            # 继续删除剩余项

    return redirect(url_for('file.file_page', parent_id=parent_id))


# 如果该 Blueprint 注册名不是 file，需要在 blueprint 注册处使用 file_bp
# app.register_blueprint(file_bp)
