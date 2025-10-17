import json
import logging
from datetime import timedelta

from flask import Flask
from flask_jwt_extended import JWTManager

from .config.log_config import init_log_config

init_log_config()

from .config import app_config
from .config.app_config import AppConfig
from .route.auth import auth_bp
from .route.main import main_bp
from .route.file import file_bp
from .route.user import user_bp
from .route.api_auth import api_auth_bp
from .route.api_file import api_file_bp


def create_app(config_mode: str = 'development'):
    flask_app = Flask(__name__)
    jwt = JWTManager()

    secret_key = 'fj@k!19qox'
    flask_app.config["JWT_SECRET_KEY"] = secret_key
    flask_app.secret_key = secret_key
    flask_app.permanent_session_lifetime = timedelta(days=5)

    jwt.init_app(flask_app)

    app_logger = logging.getLogger(AppConfig.PROJECT_NAME + "." + __name__)

    # 应用配置
    app_logger.info(f'App config mode: {config_mode}')
    flask_app.config.from_object(app_config.config_dict[config_mode])

    # 注册蓝图
    flask_app.register_blueprint(auth_bp)
    flask_app.register_blueprint(main_bp)
    flask_app.register_blueprint(file_bp)
    flask_app.register_blueprint(user_bp)
    flask_app.register_blueprint(api_auth_bp)
    flask_app.register_blueprint(api_file_bp)

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

    app_logger.info(f'APP: {AppConfig.PROJECT_NAME} Start!')
    app_logger.info(f'Config mode: {config_mode} | APP_HOST: {AppConfig.APP_HOST} | APP_PORT: {AppConfig.APP_PORT}')

    return flask_app
