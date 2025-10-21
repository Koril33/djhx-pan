import datetime
import logging
import os
import secrets
import string
from typing import Optional, Dict, Any, List

from flask import Blueprint, request, render_template, send_from_directory, redirect, url_for, flash

from ..config.app_config import AppConfig, config_dict
from ..db import DB
from ..util import safe_secure_filename, login_required, JsonResult

app_logger = logging.getLogger(AppConfig.PROJECT_NAME + "." + __name__)

app_config_mode = os.getenv("CONFIG_MODE", "development")

# 上传目录
UPLOAD_FOLDER = config_dict.get(app_config_mode).UPLOAD_FOLDER
app_logger.info("upload folder path: {}".format(UPLOAD_FOLDER))
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


PREVIEW_TYPES = {
    # 图片类
    "jpg": "image", "jpeg": "image", "png": "image", "gif": "image",
    "webp": "image", "bmp": "image", "tif": "image", "tiff": "image",
    "svg": "image", "ico": "image", "heic": "image", "avif": "image",
    "psd": "image", "ai": "image", "eps": "image",

    # 文本类
    "txt": "text", "rtf": "text",
    "xml": "text",
    "yml": "text", "toml": "text",
    "md": "text", "ini": "text",
    "env": "text", "properties": "text",
    "log": "text", "out": "text", "err": "text",

    "py": "text", "java": "text", "json": "text",
    "pyc": "text", "pyo": "text",
    "js": "text", "ts": "text", "jsx": "text", "tsx": "text",
    "html": "text", "htm": "text", "css": "text",
    "class": "text", "jar": "text",
    "c": "text", "cpp": "text", "h": "text", "hpp": "text", "cs": "text",
    "go": "text", "rs": "text", "php": "text", "rb": "text",
    "swift": "text", "kt": "text", "kts": "text", "dart": "text",
    "json5": "text", "vue": "text", "jsp": "text", "asp": "text", "aspx": "text",
    "sql": "text", "db": "text", "sqlite": "text",
    "bat": "text", "cmd": "text", "sh": "text", "bash": "text", "zsh": "text",
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
        filepath = row.get('filepath')
        if os.path.isdir(filepath):
            os.rmdir(filepath)
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
@login_required
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
@login_required
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

    if parent_id:
        parent_folder = DB.query("SELECT * FROM t_file WHERE id=?", (parent_id,))
        parent_folder = parent_folder[0] if parent_folder else None
        if parent_folder:
            save_path = os.path.join(parent_folder['filepath'], filename)

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

    preview_type = PREVIEW_TYPES.get(filetype)

    DB.execute(
        """
        INSERT INTO t_file (filename, filesize, filetype, preview_type, filepath, is_dir, parent_id, create_datetime, update_datetime)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (filename, filesize, filetype, preview_type, save_path, 0, parent_id, now, now)
    )

    # 上传后若是 fetch 提交通常会返回 200；这里统一重定向到目录页
    return redirect(url_for('file.file_page', parent_id=parent_id))


@file_bp.route('/create-folder', methods=['POST'])
@login_required
def create_folder():
    folder_name = request.form.get('folder_name')
    parent_id = request.form.get('parent_id')
    now = datetime.datetime.now().isoformat()

    parent_path = UPLOAD_FOLDER
    if parent_id:
        parent_id = int(parent_id)

        parent_folder = DB.query("SELECT * FROM t_file WHERE id=?", (parent_id,))
        parent_folder = parent_folder[0] if parent_folder else None
        if parent_folder:
            parent_path = parent_folder['filepath']

    folder_path = os.path.join(parent_path, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    if not folder_name:
        flash("文件夹名称不能为空")
        return redirect(url_for('file.file_page', parent_id=parent_id))

    # 插入目录记录（filepath 为 NULL）
    DB.execute("""
        INSERT INTO t_file (filename, filetype, filepath, is_dir, parent_id, create_datetime, update_datetime)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (folder_name, 'folder', str(folder_path), 1, parent_id if parent_id else None, now, now))

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
@login_required
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
@login_required
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



@file_bp.route('/share/<int:file_id>', methods=['POST'])
@login_required
def create_share(file_id):
    """
    创建分享链接
    接收 JSON 请求体（由前端 AJAX 发送）：
    {
        "password": "123456",  // 可选
        "expires_in": "3h",    // 可选：1h,3h,6h,12h,1d,3d,7d,never
        "allow_download": true,
        "allow_delete": false
    }
    返回 { "share_url": "/s/abc123", "error": null }
    """
    data = request.get_json()
    if not data:
        return {"error": "无效请求"}, 400

    # 验证 file_id 存在
    row = DB.query("SELECT id FROM t_file WHERE id=?", (file_id,))
    if not row:
        return {"error": "文件不存在"}, 404

    # 生成唯一 share_key (8位字母数字)
    def generate_key():
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))

    share_key = generate_key()
    max_attempts = 10
    for _ in range(max_attempts):
        if not DB.query("SELECT 1 FROM t_share WHERE share_key=?", (share_key,)):
            break
        share_key = generate_key()
    else:
        return {"error": "生成分享链接失败，请重试"}, 500

    # 处理过期时间
    expires_at = None
    expires_in = data.get('expires_in')
    if expires_in and expires_in != 'never':
        now = datetime.datetime.now()
        mapping = {
            '1h': datetime.timedelta(hours=1),
            '3h': datetime.timedelta(hours=3),
            '6h': datetime.timedelta(hours=6),
            '12h': datetime.timedelta(hours=12),
            '1d': datetime.timedelta(days=1),
            '3d': datetime.timedelta(days=3),
            '7d': datetime.timedelta(days=7),
        }
        if expires_in in mapping:
            expires_at = (now + mapping[expires_in]).isoformat()

    password = data.get('password') or None
    allow_download = bool(data.get('allow_download', True))
    allow_delete = bool(data.get('allow_delete', False))

    created_at = datetime.datetime.now().isoformat()

    DB.execute("""
        INSERT INTO t_share (file_id, share_key, password, expires_at, allow_download, allow_delete, created_datetime, update_datetime)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (file_id, share_key, password, expires_at, allow_download, allow_delete, created_at, created_at))

    share_url = url_for('file.view_share', share_key=share_key, _external=False)
    return {"share_url": share_url}


@file_bp.route('/s/<share_key>')
def view_share(share_key):
    # 查询分享记录
    shares = DB.query("SELECT * FROM t_share WHERE share_key=?", (share_key,))
    if not shares:
        return "分享链接无效或已过期", 404

    share = _row_to_dict(shares[0])

    # 检查是否过期
    if share['expires_at']:
        expire_time = datetime.datetime.fromisoformat(share['expires_at'])
        if datetime.datetime.now() > expire_time:
            return "分享链接已过期", 410

    # 检查密码（如果有）
    password = share.get('password')
    input_pwd = request.args.get('pwd')
    if password:
        if input_pwd and input_pwd != password:
            flash('密码错误', 'error')
            return render_template('share_password.html', share_key=share_key)
        elif not input_pwd:
            flash('请输入密码', 'info')
            return render_template('share_password.html', share_key=share_key)

    file_id = share['file_id']
    base_file = DB.query_one("SELECT * FROM t_file WHERE id=?", (file_id,))
    if not base_file:
        return "分享内容已被删除", 404
    base_file = _row_to_dict(base_file)

    # 获取 path 参数（如 "folder1/folder2"）
    path = request.args.get('path', '').strip('/')
    current_path_parts = [p for p in path.split('/') if p] if path else []

    # 从 base_file 开始，逐级解析 path
    current_id = base_file['id']
    breadcrumbs = []

    if base_file['is_dir']:
        # 如果分享的是目录，则根就是它
        breadcrumbs.append({'id': base_file['id'], 'filename': base_file['filename']})
        for part in current_path_parts:
            # 查找当前目录下名为 `part` 的子目录
            child = DB.query_one(
                "SELECT id, filename FROM t_file WHERE parent_id=? AND filename=? AND is_dir=1",
                (current_id, part)
            )
            if not child:
                return "路径不存在", 404
            child = _row_to_dict(child)
            breadcrumbs.append(child)
            current_id = child['id']
    else:
        # 分享的是单个文件，不允许 path 导航
        if path:
            return "无效路径", 404
        # 直接显示该文件
        base_file['icon_class'] = ICON_TYPES.get((base_file.get('filetype') or '').lower(), 'file')
        files = [base_file]
        return render_template(
            'share_view.html',
            files=files,
            is_dir_view=False,
            breadcrumbs=None,
            share=share,
            target=base_file,
            current_path=path,
            share_key=share_key
        )

    # 现在 current_id 是最终要展示的目录
    files = DB.query("SELECT * FROM t_file WHERE parent_id=?", (current_id,))
    files = [_row_to_dict(f) for f in files]
    for f in files:
        f['icon_class'] = 'folder' if f['is_dir'] else ICON_TYPES.get((f.get('filetype') or '').lower(), 'file')
    files.sort(key=lambda r: (not r['is_dir'],
                              -datetime.datetime.fromisoformat(r['create_datetime']).timestamp() if r['create_datetime'] else 0))

    return render_template(
        'share_view.html',
        files=files,
        is_dir_view=True,
        breadcrumbs=breadcrumbs,
        share=share,
        target=base_file,
        current_path=path,
        share_key=share_key,
        password=input_pwd,
    )


@file_bp.route('/share_page')
@login_required
def share_page():
    """分享管理页面"""
    shares = DB.query("""
        SELECT s.*, f.filename
        FROM t_share s
        LEFT JOIN t_file f ON s.file_id = f.id
        ORDER BY s.created_datetime DESC
    """)
    shares = [_row_to_dict(s) for s in shares]

    # 格式化字段
    for s in shares:
        s['share_url'] = url_for('file.view_share', share_key=s['share_key'], _external=False)
        if s.get('expires_at'):
            try:
                dt = datetime.datetime.fromisoformat(s['expires_at'])
                s['expires_display'] = dt.strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                s['expires_display'] = s['expires_at']
        else:
            s['expires_display'] = '永久'

    return render_template('share_page.html', shares=shares)


@file_bp.route('/share/<int:share_id>/delete', methods=['POST'])
@login_required
def delete_share(share_id):
    DB.execute("DELETE FROM t_share WHERE id=?", (share_id,))
    flash("已删除分享记录", "success")
    return redirect(url_for('file.share_page'))


@file_bp.route('/share/<int:share_id>/update', methods=['POST'])
@login_required
def update_share(share_id):
    """更新分享配置（密码、有效期、下载权限）"""
    password = request.form.get('password') or None
    expires_in = request.form.get('expires_in')
    allow_download = request.form.get('allow_download') == 'on'

    expires_at = None
    if expires_in and expires_in != 'never':
        now = datetime.datetime.now()
        mapping = {
            '1h': datetime.timedelta(hours=1),
            '3h': datetime.timedelta(hours=3),
            '6h': datetime.timedelta(hours=6),
            '12h': datetime.timedelta(hours=12),
            '1d': datetime.timedelta(days=1),
            '3d': datetime.timedelta(days=3),
            '7d': datetime.timedelta(days=7),
        }
        if expires_in in mapping:
            expires_at = (now + mapping[expires_in]).isoformat()

    DB.execute("""
        UPDATE t_share
        SET password=?, expires_at=?, allow_download=?, update_datetime=?
        WHERE id=?
    """, (password, expires_at, allow_download, datetime.datetime.now().isoformat(), share_id))

    flash("已更新分享设置", "success")
    return redirect(url_for('file.share_page'))


@file_bp.route('/public')
def public_file():
    public_shares = DB.query("""
                             SELECT t_share.id as share_id,
                                    t_file.id  as file_id,
                                    *
                             FROM t_share
                                      JOIN t_file ON t_share.file_id = t_file.id
                             WHERE password IS NULL
                               AND (expires_at IS NULL OR expires_at > ?)
                               AND t_file.is_dir = 0
                             """, (datetime.datetime.now().isoformat(),))

    public_shares = [_row_to_dict(r) for r in public_shares] if public_shares else []

    for f in public_shares:
        f['icon_class'] = 'folder' if f['is_dir'] else ICON_TYPES.get((f.get('filetype') or '').lower(), 'file')
    public_shares.sort(
        key=lambda r: (not r['is_dir'], -datetime.datetime.fromisoformat(r['create_datetime']).timestamp() if r['create_datetime'] else 0)
    )

    return JsonResult.successful('ok', data=public_shares)