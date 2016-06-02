#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'huangwei'

from flask import Blueprint, request, jsonify, make_response
from flask_restful import Api, Resource
from app.sims.models import Sims, SimsSchema
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError
from app.base_models import db

sims = Blueprint('sims', __name__)
schema = SimsSchema(strict=True)
api = Api(sims)

class CreateListSims(Resource):

    def get(self):
        icc_id = request.args.get('icc_id')
        acct_name = request.args.get('acct_name')
        order = request.args.get('order')
        per_page = int(request.args.get('per_page', 10))
        page = int(request.args.get('page', 1))
        sims_query = db.session.query(Sims)
        if icc_id:
            sims_query = sims_query.filter(Sims.icc_id == icc_id)
        if acct_name:
            sims_query = sims_query.filter(Sims.acct_name == acct_name)
        sims_query = sims_query.limit(per_page).offset(page * per_page)
        results = schema.dump(sims_query, many=True).data
        return results

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

api.add_resource(CreateListSims, '.json')
api.add_resource(GetUpdateDeleteSim, '/<int:id>.json')