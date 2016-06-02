#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'huangwei'

from extensions import celery
from base_models import db
from app.sims.models import Sims
from suds.client import Client
from suds import WebFault
from suds.wsse import Security, UsernameToken
import logging
import time
from datetime import datetime

logging.getLogger('suds.client').setLevel(logging.CRITICAL)
url = r'https://api.10646.cn/ws/schema/Terminal.wsdl'

@celery.task(bind=True)
def batch_process(self, task_id, username, password, license_key, operate):
    # 查询task 并批量调用soap接口
    security = Security()
    token = UsernameToken(username, password)
    security.tokens.append(token)
    client = Client(url)
    client.set_options(wsse=security)
    messageId = 'batch task'
    version = 1
    effective_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))

    while check_tasks(task_id):
        sim_list = db.session.query(Sims).filter(Sims.task_id == task_id, Sims.status == 0)\
            .order_by(Sims.upload_time).limit(100).all()
        for sim in sim_list:
            try:
                result = client.service.EditTerminal(messageId, version, license_key, sim.icc_id,
                                                 effective_date, operate, 3)
                # 更新该条记录状态 成功
                update_sim(sim.id, 1)
            except WebFault as detail:
                if detail.fault.faultstring == '400200':
                    # 用户名或密码错误
                    update_sim(sim.id, 200)
                elif detail.fault.faultstring == '100100':
                    # icc_id 错误
                    update_sim(sim.id, 110)
                else:
                    # 更新该条记录状态 未知异常
                    update_sim(sim.id, 100)

def check_tasks(task_id):
    return db.session.query(Sims).filter(Sims.task_id == task_id, Sims.status == 0).count() > 0

def update_sim(id, status):
    db.session.query(Sims).filter(Sims.id == id).update({
        'status': status,
        'modify_time': datetime.now()
    })
    db.session.commit()

def update_task(task_id, size):
    print(task_id + '已完成 : ' + str(size))