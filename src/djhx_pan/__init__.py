import json
import logging

from flask import Flask

from .config.log_config import init_log_config
from .extension import init_app_extension
from .util import JsonResult

init_log_config()

from .config import app_config
from .config.app_config import AppConfig
from .route.auth import auth_bp
from .route.main import main_bp
from .route.file import file_bp
from .route.user import user_bp
from .route.api_auth import api_auth_bp
from .route.api_file import api_file_bp

from .exception import ClientError, ServerError


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(file_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(api_auth_bp)
    app.register_blueprint(api_file_bp)


def create_app(config_mode: str = 'development'):
    flask_app = Flask(__name__)
    app_logger = logging.getLogger(AppConfig.PROJECT_NAME + "." + __name__)

    # 初始化应用配置和扩展
    flask_app.config.from_object(app_config.config_dict[config_mode])
    init_app_extension(flask_app)
    app_logger.info(f'App config mode: {config_mode}')

    # 注册蓝图
    register_blueprints(flask_app)

    # 全局异常处理
    @flask_app.errorhandler(500)
    def server_error(e):
        app_logger.exception(e)
        msg = f'服务异常: {e.name}'
        rv = {
            'description': str(e.description),
            'original': str(e.original_exception),
        }
        return json.dumps(rv), 500

    @flask_app.errorhandler(ClientError)
    def client_error(e):
        msg = f'错误: {e.message}'
        return JsonResult.failed(msg), 200

    @flask_app.errorhandler(ServerError)
    def server_error(e):
        app_logger.exception(e)
        msg = f'服务端错误: {e.name}'
        return JsonResult.failed(msg), 500


    app_logger.info(f'APP: {AppConfig.PROJECT_NAME} Start!')
    app_logger.info(f'Config mode: {config_mode} | APP_HOST: {AppConfig.APP_HOST} | APP_PORT: {AppConfig.APP_PORT}')

    return flask_app
