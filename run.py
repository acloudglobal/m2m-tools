#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'huangwei'

from app import create_app

app = create_app('config')

if __name__ == '__main__':
    app.run(host=app.config['HOST'],
            port=app.config['PORT'],
            debug=app.config['DEBUG'])