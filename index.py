#!/usr/bin/env python
import sys
import os

sys.path.append(os.path.dirname(__file__))

from page import parsePage

def application(environ, response):
    return parsePage(environ, response)

if __name__=='__main__':
    from wsgiref.simple_server import make_server
    httpd = make_server('', 8042, application)
    httpd.serve_forever()
