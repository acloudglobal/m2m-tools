#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'huangwei'

# DATABASE SETTINGS
# MYSQL
mysql_db_username = 'root'
mysql_db_password = '123456'
mysql_db_name = 'm2m'
mysql_db_hostname = '192.168.1.150:3306'

DEBUG = True
PORT = 5000
HOST = "0.0.0.0"
SQLALCHEMY_ECHO = False
SECRET_KEY = "SOME SECRET"

# MySQL
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_ADDR}/{DB_NAME}".format(DB_USER=mysql_db_username,
                                                                                        DB_PASS=mysql_db_password,
                                                                                        DB_ADDR=mysql_db_hostname,
                                                                                        DB_NAME=mysql_db_name)

# Celery
CELERY_BROKER_URL = 'redis://192.168.1.150:6379/0'
CELERY_RESULT_BACKEND = 'redis://192.168.1.150:6379/0'

CELERY_ALWAYS_EAGER = True