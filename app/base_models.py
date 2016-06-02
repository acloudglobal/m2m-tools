#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'huangwei'

from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class CRUD_MixIn():

    def add(self, resource):
        db.session.add(resource)
        return db.session.commit()

    def update(self):
        return db.session.commit()

    def delete(self, resource):
        db.session.delete(resource)
        return db.session.commit()