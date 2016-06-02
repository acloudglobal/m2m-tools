#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'huangwei'

from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from run import app
from app.base_models import db

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()