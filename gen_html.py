#!/usr/bin/env python

import os
import sys
from odt import ODTPage
from odt import ODT

page=1

def img(odt, fname):
    invalid = True
    if odt.open():
        data = odt.extract(fname)

        fname = fname.lower()
        if '.png' in fname:
            mime = 'image/png'
            invalid = False
        elif '.jpeg' in fname or '.jpg' in fname:
            mime = 'image/jpeg'
            invalid = False

    if invalid or data is None:
        data = ''

    return [data]

#odt = ODT(sys.argv[1])
resp = ODTPage(sys.argv[1])
pages = resp.pages()
print pages
#img(resp.odt)
while page < pages:
    #print "Page: %s" % page
    data = resp.getPage(page=page)
    #print data
    with open('page_%s.html' % page, 'w') as fd:
        fd.write(data.encode('utf-8'))
        #fd.write(data.encode('utf-8').replace('\\n', '\n'))
    page += 1

try:
    os.makedirs('img')
except:
    pass
for the_img in resp.odt.images:
    img_data = img(resp.odt, the_img)
    dd = os.path.dirname(the_img)
    try:
        os.makedirs('img/%s' % dd)
    except:
        pass
    with open('img/%s' % the_img, 'w+') as fd:
        fd.write(''.join(img_data))
    #print img
#if odt.open():
#    data = odt.extract(fname)
