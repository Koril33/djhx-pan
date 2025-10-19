import re
from datetime import datetime

from sqlalchemy.orm import validates

from ..extension import db

class BaseModel(db.Model):
    __abstract__ = True  # 👈 不会生成表
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    create_datetime = db.Column(db.DateTime, default=datetime.now)
    update_datetime = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class User(BaseModel):
    __tablename__ = "t_user"
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(12), nullable=False)
    salt = db.Column(db.String(20), nullable=False)
    nickname = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(50), unique=True, nullable=True)
    phone = db.Column(db.String(11), nullable=True)

    @validates('phone')
    def validate_phone(self, key, value):
        if not re.match(r'^\d{11}$', value):
            raise ValueError("手机号必须为11位数字")
        return value

class File(BaseModel):
    __tablename__ = "t_file"
    filename = db.Column(db.String(1024), nullable=False)
    filesize = db.Column(db.Integer, nullable=False)
    filetype = db.Column(db.String(20), nullable=False)
    filepath = db.Column(db.String(1024), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('t_file.id'), nullable=True)
    is_dir = db.Column(db.Integer, nullable=False)
    preview_type = db.Column(db.String(20), nullable=False)
    md5 = db.Column(db.String(32), nullable=True)
