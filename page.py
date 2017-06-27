import sys
import os
sys.path.append(os.path.dirname(__file__))
os.chdir(os.path.dirname(__file__))

from odt import ODTPage
from odt import ODT
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

def odtImageAction(environ, response, odt_name, rest):
    odt = ODT(odt_name)
    invalid = True
    code = '200 OK'
    if odt.open():
        fname = os.sep.join(rest)
        data = odt.extract(fname)

        fname = fname.lower()
        if '.png' in fname:
            mime = 'image/png'
            invalid = False
        elif '.jpeg' in fname or '.jpg' in fname:
            mime = 'image/jpeg'
            invalid = False

    if invalid or data is None:
        data = 'Not found'
        mime = 'text/plain'
        code = '404 Not found'

    response(code,
        [('Content-Type', mime) ]
        )
    return [data]

def parsePage(environ, response):
    extra = ""
    pars = environ['PATH_INFO']

    (action, rest) = getAction(pars)
    if action == "odt.css" or action == "odt.js" or action == "jquery.min.js":
        return fileAction(environ, response, action)

    # TODO: solve the ODT name some proper way
    odt_name = environ.get('ODT_NAME', "test.odt")
    if action == "img":
        return odtImageAction(environ, response, odt_name, rest)

    return defaultAction(environ, response, action, rest, odt_name)

def defaultAction(environ, response, action, rest, odt_name):
    if environ is not None:
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except ValueError:
            request_body_size = 0
        except AttributeError:
            request_body_size = 0
        except TypeError:
            request_body_size = 0

    request_body = environ['wsgi.input'].read(request_body_size)
    posts = parse_qs(request_body)

    page = 1
    if action[:5] == "page=":
        try:
            page = int(action[5:])
        except ValueError:
            page = 1

    resp = ODTPage(name=odt_name, dynamic=True).getPage(page=page)
    pars = environ['PATH_INFO']

    extra = []
    response('200 OK',
        [('Content-Type', 'text/html') ] + extra
        )
    return resp[2]
