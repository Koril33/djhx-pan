from .app import app
from .config.app_config import AppConfig

app.run(host=AppConfig.APP_HOST, port=AppConfig.APP_PORT, debug=False)