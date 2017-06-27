#!/usr/bin/env python

import sys
import os

sys.path.append(os.path.dirname(__file__))

from page import parsePage

import monitor
import threading

def application(environ, response):
    return parsePage(environ, response)


class palvelus(threading.Thread):
    _running = False

    def run(self):
        self._ok = False
        if palvelus._running:
            return
        palvelus._running = True
        self._ok = True
        from wsgiref.simple_server import make_server
        httpd = make_server('', 8042, application)
        while self._ok and palvelus._running:
            httpd.handle_request()

    @classmethod
    def terminate(self):
        palvelus._running = False
        self._ok = False

    @classmethod
    def isOk(self):
        return self._running

if __name__=='__main__':
    monitor.start()
    serve = palvelus()
    monitor.setServing(serve)
    serve.start()
    serve.join()
