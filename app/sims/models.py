#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'huangwei'

from marshmallow_jsonapi import Schema, fields
from marshmallow import validate
from app.base_models import db, CRUD_MixIn
import uuid

class Sims(db.Model, CRUD_MixIn):
    id = db.Column(db.String(36), primary_key=True)
    icc_id = db.Column(db.String(120), nullable=False)
    acct_name = db.Column(db.String(100), nullable=False)
    upload_time = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
    modify_time = db.Column(db.TIMESTAMP, nullable=True)
    status = db.Column(db.Integer, nullable=True)
    task_id = db.Column(db.String(36), nullable=False)

    def __init__(self, icc_id, acct_name, task_id, status=0, modify_time=None):
        self.id = str(uuid.uuid1())
        self.icc_id = icc_id
        self.acct_name = acct_name
        self.task_id = task_id
        self.status = status
        self.modify_time = modify_time

class SimsSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')
    # add validate=not_blank in required fields
    id = fields.String(dump_only=True)

    icc_id = fields.String(validate=not_blank)
    upload_time = fields.String(validate=not_blank)
    modify_time = fields.String(validate=not_blank)
    acct_name = fields.String(validate=not_blank)
    task_id = fields.String(validate=not_blank)
    status = fields.String(validate=not_blank)


    class Meta:
        type_ = 'sims'