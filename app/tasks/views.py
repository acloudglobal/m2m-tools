#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'huangwei'

from flask import Blueprint, request, jsonify, make_response
from flask_restful import Api, Resource
from app.tasks.models import Tasks, TasksSchema
from app.sims.models import Sims
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError
from app.base_models import db
import uuid
import time

tasks = Blueprint('tasks', __name__)
schema = TasksSchema(strict=True)
api = Api(tasks)

ALLOWED_EXTENSIONS = {'txt', 'csv'}

class CreateListTasks(Resource):

    def get(self):
        tasks_query = Tasks.query.all()
        results = schema.dump(tasks_query, many=True).data
        return results

    def post(self):
        file = request.files['file']
        username = request.form['username']
        password = request.form['password']
        license_key = request.form['license']
        operate = request.form['operate']
        # check params
        if file and username and password and license_key and operate:
            if allowed_file(file.filename):
                try:
                    # 批量插入tasks和sims
                    task_id = batch_insert_sims(file, username, password, license_key, operate)
                    db.session.commit()
                    # 开启自动化任务
                    from app.celery_task import batch_process
                    batch_process.delay(task_id, username, password, license_key, operate)
                except EOFError as err:
                    resp = jsonify({"error": err.message})
                    resp.status_code = 500
                    return resp
                except SQLAlchemyError as err:
                    db.session.rollback()
                    resp = jsonify({"error": err.message})
                    resp.status_code = 500
                    return resp
            else:
                resp = jsonify({'error:文件类型错误'})
                resp.status_code = 500
                return resp
        else:
            resp = jsonify({'error:参数必填'})
            resp.status_code = 500
            return resp

class GetUpdateDeleteTask(Resource):

    def get(self, id):
        task_query = Tasks.query.get_or_404(id)
        result = schema.dump(task_query).data
        return result

    def patch(self, id):
        user = Tasks.query.get_or_404(id)
        raw_dict = request.get_json(force=True)
        try:
            schema.validate(raw_dict)
            request_dict = raw_dict['data']['attributes']
            for key, value in request_dict.items():
                setattr(user, key, value)

            user.update()
            return self.get(id)

        except ValidationError as err:
            resp = jsonify({"error": err.messages})
            resp.status_code = 401
            return resp

        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            resp.status_code = 401
            return resp

    def delete(self, id):
        user = Tasks.query.get_or_404(id)
        try:
            delete = user.delete(user)
            response = make_response()
            response.status_code = 204
            return response

        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            resp.status_code = 401
            return resp

def batch_insert_sims(file, username, password, license_key, operate):
    # 设置任务信息
    task_id = str(uuid.uuid1())
    task_code = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))

    # 插入sims 2000条批量插入一次
    count = 0
    batch_size = 2000
    i = 0
    data_lines = []
    for line in file:
        (icc_id, acct_name) = line.split('\t')
        if icc_id and acct_name:
            data_lines.append({
                'id': str(uuid.uuid1()),
                'icc_id': icc_id,
                'acct_name': acct_name,
                'task_id': task_id,
                'status': 0
            })
            i = i + 1
            if i >= batch_size:
                # reset
                batch_insert(data_lines)
                count = count + i
                i = 0
                data_lines = []

    if i > 0:
        batch_insert(data_lines)
        count = count + i
        data_lines = None
    # 插入task
    db.session.add(Tasks(task_id, task_code, count, operate, 'user'))

    return task_id


def batch_insert(data_lines):
    db.engine.execute(Sims.__table__.insert(), data_lines)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

api.add_resource(CreateListTasks, '.json')
api.add_resource(GetUpdateDeleteTask, '/<int:id>.json')