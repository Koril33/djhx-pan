from ..extension import db
from ..model import File


def add_file(
        filename: str,
        filepath: str,
        is_dir: int,
        filesize: int = None,
        filetype: str = None,
        parent_id: int = None,
        preview_type: str = None,
        md5: str = None
) -> File:
    file = File(
        filename=filename,
        filesize=filesize,
        filetype=filetype,
        filepath=filepath,
        parent_id=parent_id,
        is_dir=is_dir,
        preview_type=preview_type,
        md5=md5
    )
    db.session.add(file)
    db.session.commit()
    return file

def get_file_by_md5(md5: str) -> File:
    return File.query.filter_by(md5=md5).first()


def get_file_by_id(file_id: int) -> File:
    return File.query.filter_by(id=file_id).first()


def delete_file(file_id):
    db.session.delete(get_file_by_id(file_id))
    db.session.commit()


def exist_child(file_id):
    return File.query.filter_by(parent_id=file_id).count() != 0