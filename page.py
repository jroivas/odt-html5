import sys
import os
sys.path.append(os.path.dirname(__file__))
os.chdir(os.path.dirname(__file__))

from odt import ODTPage
from cgi import parse_qs, escape

def getAction(s):
    if s[:1]=='/':
        s = s[1:]
    parts = s.split("/")
    action=""
    if len(parts)>0:
        action = parts[0]
    if len(parts)>1:
        rest = parts[1:]
    else:
        rest = []
    return (action, rest)

def fileAction(environ, response, filename):
    try:
        f = open(filename)
        data = f.read()
        f.close()
    except IOError:
        data = ""
    except OSError:
        data = ""
    response('200 OK',
        [('Content-Type', 'text/plain') ]
        )
    return [data]

def parsePage(environ, response):
    extra = ""
    pars = environ['PATH_INFO']
    (action, rest) = getAction(pars)
    if action == "odt.css" or action == "odt.js" or action == "jquery.min.js":
        return fileAction(environ, response, action)

    return defaultAction(environ, response)

def defaultAction(environ, response):
    if environ!=None:
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except ValueError:
            request_body_size = 0
        except AttributeError:
            request_body_size = 0
        except TypeError:
            request_body_size = 0

        #gets = parse_qs(environ['QUERY_STRING'])

    request_body = environ['wsgi.input'].read(request_body_size)
    posts = parse_qs(request_body)

    #logout = posts.get('logout', [])
    resp = ODTPage().getPage()
    pars = environ['PATH_INFO']

    extra = []
    response('200 OK',
        [('Content-Type', 'text/html') ] + extra
        )
    return [resp]
