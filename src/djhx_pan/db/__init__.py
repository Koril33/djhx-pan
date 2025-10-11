import logging
import os
import sqlite3

from ..config.app_config import config_dict, AppConfig

app_logger = logging.getLogger(AppConfig.PROJECT_NAME + "." + __name__)
app_config_mode = os.getenv("CONFIG_MODE", "development")


DB_PATH = config_dict.get(app_config_mode).DB_NAME
app_logger.info("DB path: {}".format(DB_PATH))

class DB:
    @staticmethod
    def get_connection():
        """获取 SQLite3 数据库连接"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def execute(sql, params=None):
        """执行单条语句（适用于 INSERT/UPDATE/DELETE）"""
        conn = DB.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(sql, params or [])
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()

    @staticmethod
    def query(sql, params=None):
        """执行查询语句，返回结果列表（字典形式）"""
        conn = DB.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(sql, params or [])
            rows = cur.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    @staticmethod
    def query_one(sql, params=()):
        rows = DB.query(sql, params)
        return rows[0] if rows else None
