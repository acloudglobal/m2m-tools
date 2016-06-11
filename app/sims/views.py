#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'huangwei'

from flask import Blueprint, request, jsonify, make_response
from flask_restful import Api, Resource
from app.sims.models import Sims, SimsSchema
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError
from app.base_models import db
import time

sims = Blueprint('sims', __name__)
schema = SimsSchema(strict=True)
api = Api(sims)

class CreateListSims(Resource):

    def get(self):
        # 获取请求中的参数
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        try:
            start_date = convert_date(start_date_str)
            end_date = convert_date(start_date_str)
            per_page = int(request.args.get('per_page', 10))
            page = int(request.args.get('page', 1))
        except Exception as err:
            resp = jsonify({"error": err.message})
            resp.status_code = 500
            return resp

        # 创建查询
        sims_query = db.session.query(Sims)
        if start_date:
            sims_query = sims_query.filter(Sims.upload_time > start_date)
        if end_date:
            sims_query = sims_query.filter(Sims.upload_time < end_date)
        # if acct_name:
        #     sims_query = sims_query.filter(Sims.acct_name.like('%' + acct_name + '%'))
        count = sims_query.count()
        sims_query = sims_query.order_by(Sims.upload_time.desc()).limit(per_page).offset((page - 1) * per_page)
        results = schema.dump(sims_query, many=True).data
        # result
        resp = jsonify({
            "data": results,
            'total_count': count
        })
        resp.status_code = 200
        return resp

class GetUpdateDeleteSim(Resource):

    def get(self, id):
        sim_query = Sims.query.get_or_404(id)
        result = schema.dump(sim_query).data
        return result

    def patch(self, id):
        sim = Sims.query.get_or_404(id)
        raw_dict = request.get_json(force=True)
        try:
            schema.validate(raw_dict)
            request_dist = raw_dict['data']['attributes']
            for key, value in request_dist.items():
                setattr(sim, key, value)

            sim.update()
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
        user = Sims.query.get_or_404(id)
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

def convert_date(date_str):
    if date_str:
        return time.strftime('%Y-%m-%d', time.strptime(date_str[:-15], "%a %b %d %Y %H:%M:%S"))
    return None


api.add_resource(CreateListSims, '.json')
api.add_resource(GetUpdateDeleteSim, '/<int:id>.json')