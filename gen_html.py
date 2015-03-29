#!/usr/bin/env python

import os
import sys
from odt import ODTPage
from odt import ODT

page=1
pagename='sivu'

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
odt = ODTPage(sys.argv[1], pagename=pagename)
pages = odt.pages()
print pages
title = 'Ymmyrk&auml;inen'
predata = ''
got_title = False
while page <= pages:
    if not got_title:
        prev_page = 'index.html'
    else:
        prev_page = got_title
    (page_title, content, data) = odt.getPage(page=page, title=title, prev_page=prev_page)
    if got_title or page_title:
        with open('%s_%s.html' % (pagename, page), 'w') as fd:
            fd.write(data.encode('utf-8'))
        got_title = True
    else:
        predata += content

    page += 1

with open('index.html', 'w') as fd:
    fd.write(odt.genIndex(title, predata).encode('utf-8'))

try:
    os.makedirs('img')
except:
    pass
for the_img in odt.odt.images:
    img_data = img(odt.odt, the_img)
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
