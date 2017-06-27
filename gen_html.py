#!/usr/bin/env python

import argparse
import os
import sys
from odt import ODTPage
from odt import ODT


class HTMLGenerator:
    def __init__(self, odtfile, page=1, pagename='page', title='Title', index=None):
        self.page = page
        self.pagename = pagename
        self.title = title
        self.index = index
        self.gen_index = index is not None
        if not self.gen_index:
            self.index = "%s_1" % self.pagename
        self.odt = ODTPage(odtfile, pagename=self.pagename, indexname=self.index)

    def img(self, fname):
        invalid = True
        if self.odt.odt.open():
            data = self.odt.odt.extract(fname)

            fname = fname.lower()
            if '.png' in fname:
                mime = 'image/png'
                invalid = False
            elif '.jpeg' in fname or '.jpg' in fname:
                mime = 'image/jpeg'
                invalid = False

        if invalid or data is None:
            data = ''

        return data

    def generateHTML(self):
        pages = self.odt.pages()
        print pages
        predata = ''
        got_title = False
        while self.page <= pages:
            if self.gen_index and not got_title:
                prev_page = '%s.html' % self.index
            else:
                prev_page = got_title
            (page_title, content, data) = self.odt.getPage(page=self.page, title=self.title, prev_page=prev_page)
            if not self.gen_index or got_title or page_title:
                with open('%s_%s.html' % (self.pagename, self.page), 'w') as fd:
                    fd.write(data.encode('utf-8'))
                got_title = True
            else:
                predata += content

            self.page += 1

        if self.gen_index:
            with open('%s.html' % self.index, 'w') as fd:
                fd.write(self.odt.genIndex(self.title, predata).encode('utf-8'))

        try:
            os.makedirs('img')
        except:
            pass
        for the_img in self.odt.odt.images:
            img_data = self.img(the_img)
            dd = os.path.dirname(the_img)
            try:
                os.makedirs('img/%s' % dd)
            except:
                pass
            with open('img/%s' % the_img, 'w+') as fd:
                fd.write(img_data)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ODT-HTML5')
    parser.add_argument('-t', '--title', default='Title', help='Title')
    parser.add_argument('-p', '--prefix', default='page', help='Page prefix')
    parser.add_argument('-i', '--index', default=None, help='Generate index with')
    parser.add_argument('filename', help='Input ODT')
    args = parser.parse_args()

    g = HTMLGenerator(args.filename, pagename=args.prefix, index=args.index, title=args.title)

    g.generateHTML()
