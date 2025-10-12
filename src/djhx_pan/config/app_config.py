import platform


class AppConfig(object):
    # 存储公共配置
    PROJECT_NAME = "djhx-pan"

    APP_HOST = "0.0.0.0"
    APP_PORT = 8125
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024
    MAX_FORM_MEMORY_SIZE = 100 * 1024 * 1024


class DevelopmentConfig(AppConfig):
    # 存储开发环境中的配置
    if platform.system().lower() == 'windows':
        DB_NAME = "C:\\Project\\MyProject\\djhx-pan\\djhx-pan.db"
        UPLOAD_FOLDER = "C:\\Project\\MyProject\\djhx-pan\\uploads"
    else:
        DB_NAME = "/home/koril/project/python/djhx-pan/djhx-pan.db"
        UPLOAD_FOLDER = "/home/koril/project/python/djhx-pan/uploads"


class ProductionConfig(AppConfig):
    # 存储生产环境中的配置
    DB_NAME = "/home/koril/project/djhx-pan/djhx-pan.db"
    UPLOAD_FOLDER = "/home/koril/project/djhx-pan/uploads"

config_dict = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}
