#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'huangwei'

from flask import Flask
from flask_cors import CORS

def create_app(config_filename):
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    app.config.from_object(config_filename)

    from app.base_models import db
    db.init_app(app)

    from app.extensions import celery
    celery.init_app(app)

    from app.sims.views import sims
    app.register_blueprint(sims, url_prefix='/api/sims')

    from app.tasks.views import tasks
    app.register_blueprint(tasks, url_prefix='/api/tasks')

    with app.app_context():
        db.create_all()

    return app