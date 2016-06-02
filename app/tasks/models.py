#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'huangwei'

from marshmallow_jsonapi import Schema, fields
from marshmallow import validate
from app.base_models import db, CRUD_MixIn
import uuid

class Tasks(db.Model, CRUD_MixIn):
    id = db.Column(db.String(36), primary_key=True)
    task_code = db.Column(db.String(14), nullable=False, unique=True)
    task_size = db.Column(db.Integer, nullable=False)
    task_operate = db.Column(db.String(20), nullable=False)
    modify_user = db.Column(db.String(32), nullable=False)

    def __init__(self, task_id, task_code, task_size, task_operate, modify_user):
        self.id = task_id
        self.task_code = task_code
        self.task_size = task_size
        self.task_operate = task_operate
        self.modify_user = modify_user


class TasksSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')
    # add validate=not_blank in required fields
    id = fields.String(dump_only=True)

    task_code = fields.String(validate=not_blank)
    task_size = fields.Integer(validate=not_blank)
    task_operate = fields.String(validate=not_blank)
    modify_user = fields.String(validate=not_blank)

    class Meta:
        type_ = 'tasks'
