import hashlib
import os

from werkzeug.datastructures import FileStorage

from ..config.log_config import project_logger
from ..config.app_config import config_dict
from ..exception import ClientError
from ..repository import file_repo
from ..util.constant import PREVIEW_TYPES

app_logger = project_logger()

app_config_mode = os.getenv("CONFIG_MODE", "development")
UPLOAD_FOLDER = config_dict.get(app_config_mode).UPLOAD_FOLDER
app_logger.info("upload folder path: {}".format(UPLOAD_FOLDER))
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def save_file(file: FileStorage, parent_id: str, md5: str) -> None:
    if not file.filename:
        raise ClientError(f'上传文件的文件名不能为空')

    parent_path = UPLOAD_FOLDER
    if parent_id:
        parent_id = int(parent_id)

        parent_file = file_repo.get_file_by_id(parent_id)
        if not parent_file:
            raise ClientError(f'上传文件的父级目录不存在')

        if not parent_file.is_dir:
            raise ClientError(f'父级节点需要是目录')
        parent_path = parent_file.filepath


    filename = file.filename
    save_path = os.path.join(parent_path, filename)

    file.save(save_path)
    # 服务端重新计算 MD5
    temp_md5 = hashlib.md5()
    with open(save_path, "rb") as fp:
        for chunk in iter(lambda: fp.read(8192), b""):
            temp_md5.update(chunk)
    server_md5 = temp_md5.hexdigest()

    # 校验一致性
    if md5 != server_md5:
        raise ClientError(f'{filename} md5 不匹配')

    filesize = os.path.getsize(save_path)
    _, ext = os.path.splitext(filename)
    filetype = ext.lstrip('.').lower() if ext else ''

    preview_type = PREVIEW_TYPES.get(filetype)

    file_repo.add_file(
        filename=filename,
        filetype=filetype,
        filesize=filesize,
        preview_type=preview_type,
        md5=md5,
        parent_id=parent_id,
        filepath=save_path,
        is_dir=0
    )


def save_folder(folder_name, parent_id):
    if not folder_name:
        raise ClientError(f'目录名称不能为空')

    parent_path = UPLOAD_FOLDER
    if parent_id:
        parent_id = int(parent_id)

        parent_file = file_repo.get_file_by_id(parent_id)
        if not parent_file:
            raise ClientError(f'上传文件的父级目录不存在')

        if not parent_file.is_dir:
            raise ClientError(f'父级节点需要是目录')
        parent_path = parent_file.filepath

    folder_path = os.path.join(parent_path, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    file_repo.add_file(
        filename=folder_name,
        filetype='folder',
        parent_id=parent_id,
        filepath=str(folder_path),
        is_dir=1
    )


def download_file(file_id) -> str:
    file = file_repo.get_file_by_id(file_id)
    if not file:
        raise ClientError(f'文件 id {file_id} 不存在')

    if file.is_dir:
        raise ClientError(f'无法下载目录')

    filepath = file.filepath
    if not filepath:
        raise ClientError(f'无法下载: 未找到文件 id {file_id} 路径')

    return filepath


def delete_file(file_id):
    target_file = file_repo.get_file_by_id(file_id)
    if not target_file:
        raise ClientError(f'文件 id {file_id} 无法找到')

    if target_file.is_dir:
        raise ClientError(f'接口调用错误，该接口无法删除目录')

    target_filepath = target_file.filepath
    if target_filepath and os.path.exists(target_filepath) and os.path.isfile(target_filepath):
        os.remove(target_filepath)
        file_repo.delete_file(file_id)
        return target_file
    else:
        raise ClientError(f'删除文件 id {file_id} 异常')


def delete_folder(folder_id):
    target_folder = file_repo.get_file_by_id(folder_id)
    if not target_folder:
        raise ClientError(f'目录 id {folder_id} 无法找到')

    if not target_folder.is_dir:
        raise ClientError(f'接口调用错误，该接口无法删除文件')

    if file_repo.exist_child(folder_id):
        raise ClientError(f'该目录下存在子文件，无法删除目录')

    target_folder_path = target_folder.filepath
    if target_folder_path and os.path.exists(target_folder_path) and os.path.isdir(target_folder_path):
        os.rmdir(target_folder_path)
        file_repo.delete_file(folder_id)
        return target_folder
    else:
        raise ClientError(f'删除目录 id {folder_id} 异常')