#!/usr/bin/env python

import argparse
import os
from odt import ODTPage


class HTMLGenerator:
    def __init__(self, odtfile, page=1, pagename='page', title='Title', index=None):
        self.page = page
        self.pagename = pagename
        self.title = title
        self.index = index
        self.gen_index = index is not None
        self.pages = 0
        if not self.gen_index:
            self.index = "%s_1" % self.pagename
        self.odt = ODTPage(odtfile, pagename=self.pagename, indexname=self.index)
        self.got_title = False
        self.prev_page = False
        self.index_data = ''
        self.data = ''
        self.content = ''

    def isOdtFileOpen(self):
        return self.odt.odt.open()

    def extractFileFromOdt(self, fname):
        if self.isOdtFileOpen():
            return self.odt.odt.extract(fname)
        return None

    def detectFileMime(self, fname):
        fname = fname.lower()
        if '.png' in fname:
            return 'image/png'
        elif '.jpeg' in fname or '.jpg' in fname:
            return 'image/jpeg'
        return None

    def isValidFile(self, fname):
        return self.detectFileMime(fname) is not None

    def img(self, fname):
        if self.isValidFile(fname):
            data = self.extractFileFromOdt(fname)

        if data is None:
            data = ''

        return data

    def isPagesLeft(self):
        return self.page <= self.pages

    def countPages(self):
        self.pages = self.odt.pages()

    def isNormalPage(self):
        return not self.gen_index or self.got_title or self.page_title

    def resolvePreviousPage(self):
        if self.gen_index and not self.got_title:
            self.prev_page = '%s.html' % self.index
        else:
            self.prev_page = self.got_title

    def writePage(self):
        with open('%s_%s.html' % (self.pagename, self.page), 'w') as fd:
            fd.write(self.data.encode('utf-8'))
        self.got_title = True

    def appendIndexData(self):
        self.index_data += self.content

    def nextPage(self):
        self.page += 1

    def getPageContentsInUtf8(self):
        return self.odt.genIndex(self.title, self.index_data).encode('utf-8')

    def writeIndexPage(self):
        if self.gen_index:
            with open('%s.html' % self.index, 'w') as fd:
                fd.write(self.getPageContentsInUtf8())

    def getPage(self):
        (self.page_title, self.content, self.data) = self.odt.getPage(page=self.page, title=self.title, prev_page=self.prev_page)

    def makeImageFolder(self, extra=''):
        try:
            os.makedirs('img/%s' % extra)
        except:
            pass

    def getImageData(self, img):
        self.img_data = self.img(img)

    def writeImage(self, img):
        with open('img/%s' % img, 'w+') as fd:
            fd.write(self.img_data)

    def generateImages(self):
        for img in self.odt.odt.images:
            self.getImageData(img)
            self.makeImageFolder(os.path.dirname(img))
            self.writeImage(img)

    def generatePage(self):
        self.resolvePreviousPage()
        self.getPage()
        if self.isNormalPage():
            self.writePage()
        else:
            self.appendIndexData()

        self.nextPage()

    def generatePages(self):
        while self.isPagesLeft():
            self.generatePage()
        self.writeIndexPage()

    def generateHTML(self):
        self.countPages()
        self.generatePages()
        self.generateImages()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ODT-HTML5')
    parser.add_argument('-t', '--title', default='', help='Title')
    parser.add_argument('-p', '--prefix', default='page', help='Page prefix')
    parser.add_argument('-i', '--index', default=None, help='Generate index with')
    parser.add_argument('filename', help='Input ODT')
    args = parser.parse_args()

    g = HTMLGenerator(args.filename, pagename=args.prefix, index=args.index, title=args.title)

    g.generateHTML()
