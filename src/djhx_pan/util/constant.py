
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