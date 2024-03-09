from multiprocessing import Value

from flask import Flask
from gunicorn.app.base import BaseApplication

from .routes import app_blueprint

lock = Value("i", 0)


def create_app():
    app = Flask(__name__)
    app.register_blueprint(app_blueprint)
    app.config["lock"] = lock
    return app


app = create_app()


class StandaloneApplication(BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


options = {
    "bind": "0.0.0.0:8080",
    "workers": 4,
}
StandaloneApplication(app, options).run()
