import zipfile
import os
import xml.etree.ElementTree as etree
import re
import copy

class ODTPage:
    def __init__(self, name, odt=None, pagename='page', indexname='index', dynamic=False):
        self.pagename = pagename
        self.indexname = indexname
        if odt is None:
            self.odt = ODT(name)
        else:
            self.odt = odt

        self.index = []
        self.dynamic = dynamic

    def pages(self):
        return self.odt.pageCount()

    def getTitle(self):
        for i in self.odt.titles:
            return (i, self.odt.titles[i][0])
        return (0, '')

    def getPage(self, page=1, title="ODT", prev_page=True):
        res = ''
        self.odt.reset()
        pages = self.odt.pageCount()
        if page > pages:
            page = pages
        if page < 1:
            page = 1
        styles = self.getStyles(pages, page)
        content = self.getContent(self.odt, page)
        body = self.getBody(self.odt, page, content, prev_page, title)
        (level, page_title) = self.getTitle()
        if page_title:
            title += ' - ' + page_title
            self.index.append((level, page, page_title))

        head = '<!-- AAA --> ' + self.getHeader(title, styles) + '<!-- BBB -->'
        foot = self.getFooter()
        foot = ""
        return page_title, content, head + body + foot

    def genIndex(self, title, extra):
        res = '<body>\n'
        res += extra
        res += '<div class="page">\n'
        for level, page, target in self.index:
            res += '<div>%s<a href="%s_%s.html">%s</a></div>\n' % ('&nbsp;' * 2 * int(level), self.pagename, page, target)
        res += '</div>\n'
        res += '</body>\n'

        head = self.getHeader(title, '')
        foot = self.getFooter()
        return head + res + foot

    def getStyles(self, pagecnt, curpage=1):
        return ""
        res = "<style>\n"
        i = 1
        while i <= pagecnt:
            res += "div.pageNum%s {\n" % (i)
            if i != curpage:
                res += "\tdisplay: none;\n"
            res += "\tzIndex: 1;\n"
            res += "\tposition: absolute;\n"
            res += "}\n"
            i += 1
        res += "</style>\n"
        return res

    def getHeader(self, title, extra=""):
        return """<html>
        <head>
            <title>%s</title>
            <link rel="stylesheet" type="text/css" title="styles" href="odt.css"/>
            <meta charset="UTF-8">
            <script type="text/javascript" src="jquery.min.js"></script>
            <script type="text/javascript" src="odt.js"></script>
            %s
        </head>
        """ % (title, extra)
        #<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js"></script>

    def getContent(self, odt, page):
        res = odt.read()
        tmp = ''
        if not res:
            return "<p>Invalid file</p>"

        tmp = odt.parseContent(page=page)

        return """
        <!-- START -->
        <div class="page">
            %s
        </div>
        <!-- END -->
        """ % (''.join(tmp))

    def getBody(self, odt, page, content, prev_page, title):
        cntx = ''
        cntx += '<a href="%s.html"><div id="top_left">%s</div></a>\n' % (self.indexname, title)
        #cntx += '<div id="top_right">&nbsp;</div>\n'
        if prev_page and page > 1:
            if prev_page == True:
                if self.dynamic:
                    prev_page = "?page=" % (page - 1)
                else:
                    prev_page = "%s_%s.html" % (self.pagename, page - 1)
            cntx += """
        <!-- PREV --><a href="%s">
        <div id='prevPage'>
        &lt;&lt;
        </div></a>
        """ % (prev_page)

        cntx += """
        <input type='hidden' id='pagenum' name='pagenum' value='%s'></input>
        <input type='hidden' id='pagecnt' name='pagecnt' value='%s'></input>
        """ % (page, odt.pageCount())

        cntx += "<div id='pageDiv'>\n"

        cntx += content
        #cntx += self.getContent(odt, page)

        cntx += "</div>\n"
        if page < odt.pageCount():
            if self.dynamic:
                cntx += """
        <!-- NEXT --><a href="?page=%s">
        <div id='nextPage'>
        &gt;&gt;
        </div>
        </a>
        """ % (page + 1)
            else:
                cntx += """
        <!-- NEXT --><a href="%s_%s.html">
        <div id='nextPage'>
        &gt;&gt;
        </div>
        </a>
        """ % (self.pagename, page + 1)

        return """
        <body>
            %s
        </body>
""" % (cntx)

    def getFooter(self):
        return """</html>"""

class ODT:
    def __init__(self, name):
        self._name = name
        self._page = 1
        self._zip = None
        self._styles = {}
        self._styles_xml = None
        self._content_xml = None
        self._stylename = None
        self._read = False
        self._read = self.read()
        self._pagecnt = None
        self._lists = {}
        self._hlevels = {}
        self._localtargets = {}
        self._framedata = None
        self._listname = None
        self._tab = None
        self._stylestack = []
        self._imageframe1 = ''
        self._imageframe1_end = ''
        self._imageframe2 = ''
        self._imageframe2_end = ''
        self.images = []
        self.titles = {}
        #self._pagedata = {}
        self.tabs = []

    def reset(self):
        self.titles = {}
        self._page = 1

    def open(self):
        if not os.path.isfile(self._name):
            self._zip = None
            return False
        try:
            self._zip = zipfile.ZipFile(self._name, 'r')
        except zipfile.BadZipfile:
            self._zip = None
            return False
        return True

    def close(self):
        self._zip.close()

    def extract(self, file):
        if self._zip == None:
            return None
        try:
            return self._zip.read(file)
        except KeyError:
            return None

    def cleanTag(self, tag):
        return re.sub("{[^}]+}","",tag).strip()

    def findElement(self, root, name):
        res = []
        #if self.cleanTag(root.tag) == name:
        if root.tag == name:
            res.append(root)
        for child in root:
            if child.tag == name:
                res.append(child)
            tmp = self.findElement(child, name)
            for item in tmp:
                if item not in res:
                    res.append(item)
        return res

    def parseStyleTag(self, styles):
        res = {}
        for style in styles:
            tmp = self.getAttrib(style, "name")
            if tmp is not None:
                res[tmp] = {}
                self._stylename = tmp
            elif self._stylename not in res:
                res[self._stylename] = {}

            pstyle = self.getAttrib(style, "parent-style-name")
            if pstyle is not None and res is not None:
                res[self._stylename]["parent"] = pstyle
            text_prop = self.parseTextProperties(style)
            if text_prop:
                res[self._stylename]["text-prop"] = text_prop

            para_prop = self.parseParagraphProperties(style)
            if para_prop:
                res[self._stylename]["para-prop"] = para_prop
        return res

    def filterAttributes(self, props, keep):
        res = []
        for prop in props:
            style = {}
            for val in prop.attrib:
                if val in keep:
                    style[val] = prop.attrib[val]

            if style:
                res.append(style)

        if len(res) == 1:
            return res[0]
        return res

    def parseTextPropertyTag(self, props):
        valid_text_attrs = ["font-size", "color", "background-color", "font-weight",
            "font-style", "text-underline-style", "text-underline-color",
            "text-overline-style", "text-line-through-style" ]

        return self.filterAttributes(props, valid_text_attrs)

    def parseParagraphPropertyTag(self, props):
        valid_para_attrs = [ "break-before", "text-align", "color", "background-color",
            "text-indent", "margin-left", "margin-right", "margin-top", "margin-bottom" ]

        return self.filterAttributes(props, valid_para_attrs)

    def getAttrib(self, tag, name):
        for attrib in tag.attrib:
            #if self.cleanTag(attrib)==name:
            if attrib == name:
                return tag.attrib[attrib]
        return None

    def stripNamespace(self, root):
        for el in root.getiterator():
            if el.tag[0] == "{":
                el.tag = el.tag.split('}', 1)[1]
            tmp = {}
            for attr in el.attrib:
                if attr[0] == "{":
                    tmp[attr.split('}', 1)[1]] = el.attrib[attr]
                else:
                    tmp[attr] = el.attrib[attr]
            el.attrib = tmp

    def parseStyleXML(self):
        if self._styles_xml == None:
            return None
        self._style_root = etree.fromstring(self._styles_xml)
        self.stripNamespace(self._style_root)

    def parseContentXML(self):
        if self._content_xml == None:
            return None
        self._content_root = etree.fromstring(self._content_xml)
        self.stripNamespace(self._content_root)

    def parseXML(self):
        self.parseStyleXML()
        self.parseContentXML()

    def parseParagraphProperties(self, item=None):
        if item is None:
            item = self._style_root
        tags = self.findElement(item, "paragraph-properties")
        return self.parseParagraphPropertyTag(tags)

    def parseTextProperties(self, item=None):
        if item is None:
            item = self._style_root
        tags = self.findElement(item, "text-properties")
        return self.parseTextPropertyTag(tags)

    def parseStyles(self):
        styles = self.findElement(self._style_root, "style")
        return self.parseStyleTag(styles)

    def getAttrib(self, item, attr):
        if not attr in item.attrib:
            return None
        return item.attrib[attr]

    def parseContent(self, page=0):
        return self.parseTag(self._content_root, page=page),

    def parseStyle(self, style):
        res = ""
        extra = False
        if "text-prop" in style:
            for key in style["text-prop"]:
                if extra:
                    res += " "
                extra = True
                if key == "text-underline-style":
                    res += "text-decoration: underline;" 
                elif key == "text-overline-style":
                    res += "text-decoration: overline;" 
                elif key == "text-line-through-style":
                    res += "text-decoration: line-through;" 
                else:
                    res += "%s: %s;" % (key, style["text-prop"][key].strip()) 
        if "para-prop" in style:
            for key in style["para-prop"]:
                if extra:
                    res += " "
                extra = True
                if key == "text-indent":
                    res += "padding-left: %s;" % (style["para-prop"][key].strip())
                elif key == "break-before":
                    pass
                else:
                    res += "%s: %s;" % (key, style["para-prop"][key].strip()) 
        if "tab" in style:
            if style["tab"]["pos"] is not None:
                res += "margin-left: %s;" % (style["tab"]["pos"])
        return res

    def isBreak(self, style):
        if style is None:
            return False
        if not "para-prop" in style:
            return False
        if "break-before" in style["para-prop"] and style["para-prop"]["break-before"] == "page":
            return True
        return False

    def isInternalLink(self, link):
        if link[0] == "#":
            return True
        return False

    def parseInternalLink(self, link):
        if link[0] != "#":
            return link
        data = link[1:].split("|")
        return data[0]

    def parseLink(self, link):
        intlink = self.parseInternalLink(link)
        if intlink in self._localtargets:
            page = 'page=%s' % (self._localtargets[intlink]) + '#'
        else:
            page = ''
        return page+intlink

    def setupLevel(self, level):
        nlevel = int(level)
        if not level in self._hlevels:
            self._hlevels[level] = 0
        self._hlevels[level] += 1
        tmp = nlevel + 1
        while tmp <= 6:
            self._hlevels["%s" % tmp] = 0
            tmp += 1

    def levelLabel(self, level):
        lab = ""
        tmp = 1
        while tmp < 6:
            levnum = self._hlevels["%s" % tmp]
            if levnum == 0:
                break
            lab += "%s." % (levnum)
            tmp += 1
        return lab

    def solveStyle(self, item, style=None):
        combined = {}
        if style is None:
            style = self.getAttrib(item, "style-name")
        styledata = self.getStyle(style)

        extra = ""
        if styledata is not None:
            cstyledata = copy.deepcopy(styledata)

            # Solve style stack
            stack = [cstyledata]
            pstack = []
            while cstyledata is not None and "parent" in cstyledata:
                parstyle = cstyledata["parent"]
                #if parstyle in pstack:
                #    break
                pstack.append(parstyle)
                pardata = self.getStyle(parstyle)
                if pardata is not None:
                    stack.append(copy.deepcopy(pardata))
                cstyledata = pardata

            solved_style = {}
            while stack:
                data = stack.pop()
                tmp = {}
                tmp[style] = data
                self.mergeStyles(tmp, solved_style)

            parsedstyle = self.parseStyle(solved_style[style])
            if parsedstyle:
                extra = ' style="%s"' % (parsedstyle)
        return extra

    def handleTail(self, item):
        if item.tail is not None:
            return item.tail
        return ""

    def mergeStyles(self, updater, dest=None):
        if not updater:
            return
        if dest is None:
            dest = self._styles

        for k in updater:
            if not k in dest:
                dest[k] = updater[k]
            else:
                if "text-prop" in updater[k]:
                    if not "text-prop" in dest[k]:
                        dest[k]["text-prop"] = {}
                    dest[k]["text-prop"].update(updater[k]["text-prop"])
                if "para-prop" in updater[k]:
                    if not "para-prop" in dest[k]:
                        dest[k]["para-prop"] = {}
                    dest[k]["para-prop"].update(updater[k]["para-prop"])
                if "parent" in updater[k]:
                    dest[k]["parent"] = updater[k]["parent"]

    def parseTag(self, item, page=1):
        listname = None
        res = ""
        res_start = ''
        res_close = ''

        style = self.getAttrib(item, "style-name")
        styledata = self.getStyle(style)
        if self.isBreak(styledata):
            self._page += 1
            #res += "</div>\n"
            #res += '<div class="pageNum%s" id="pageNum%s">\n' % (self._page, self._page)


        if self._page != page:
            #print self._page, page
            tmp = ''
            for ch in item:
                tmp += self.parseTag(ch, page=page)
            return res + tmp
        #else:
            #res += "\n<!--begin-->\n<div>\n"

        if item.tag == "list-style":
            listname = self.getAttrib(item, "name")
            if not listname in self._styles:
                self._styles[listname] = {}
            self._listname = listname
        elif item.tag == "list-level-style-bullet":
            bullet = self.getAttrib(item, "bullet-char")
            if self._listname is not None:
                self._styles[self._listname]["bullet"] = bullet
        elif item.tag == "paragraph-properties" or item.tag == "text-properties":
            extra = self.parseStyleTag([item])
            self.mergeStyles(extra)
        elif item.tag == "style":
            self._stylename = self.getAttrib(item, "name")
            self._stylestack.append(self._stylename)
            self._parentname = self.getAttrib(item, "parent-style-name")
        elif item.tag == "list":
            stylename = self.getAttrib(item, "style-name")
            style = self.getStyle(stylename)
            if style is not None and "bullet" in style:
                res += "<ul>"
                res_close += "</ul>"
            else:
                res += "<ol>"
                res_close += "</ol>"
        elif item.tag == "list-item":
            res += "<li>"
            res_close += "</li>"
        elif item.tag == "a":
            href = self.getAttrib(item, "href")
            if href is not None:
                extra = self.solveStyle(item)
                res += '<a href="%s"%s>' % (self.parseLink(href), extra)
                res_close += "</a>"
        elif item.tag == "frame":
            frame = {}
            frame["style"] = self.solveStyle(item)
            frame["anchor"] = self.getAttrib(item, "anchor")
            frame["width"] = self.getAttrib(item, "width")
            frame["height"] = self.getAttrib(item, "height")
            self._framedata = frame
        elif item.tag == "imageframe":
            style = self.solveStyle(item)
            self._imageframe1 = '<span%s>' % (extra)
            self._imageframe1_end = '</span>'
            self._imageframe2 = '<div%s>' % (extra)
            self._imageframe2_end = '</div>'
        elif item.tag == "image":
            href = self.getAttrib(item, "href")
            if href is not None:
                self.images.append(href)
                if self._framedata is not None:
                    img_styles = ""
                    p_styles = ""
                    if self._framedata["width"] is not None:
                        img_styles += "width: %s;" % (self._framedata["width"])
                    _anchor = self._framedata["anchor"]
                    if self._framedata["height"] is not None:
                        img_styles += "height: %s;" % (self._framedata["height"])
                        if _anchor == "paragraph":
                            p_styles += "margin-bottom: -%s;" % (self._framedata["height"])
                    imgextra = ""
                    if img_styles:
                        imgextra = ' style="%s;"' % (img_styles)
                    extra = ""
                    if p_styles:
                        extra = ' style="%s"' % (p_styles)

                    src = "img/%s" % (href)
                    imgdata = '<img src="%s"%s>' % (src, imgextra)
                    imgdata_end = '</img>'
                    if _anchor == "as-is":
                        res += self._imageframe1
                        res += imgdata
                        res_close += imgdata_end
                        res_close += self._imageframe1_end
                    else:
                        res += self._imageframe2
                        res += imgdata
                        res_close += imgdata_end
                        res_close += self._imageframe2_end
                    #if _anchor == "as-is":
                    #    res += '<span%s>%s</span>' % (extra, imgdata)
                    #else:
                    #    res += '<div%s>%s</div>' % (extra, imgdata)
        elif item.tag == "tab-stop":
            tab = {}
            tab["pos"] = self.getAttrib(item, "position")
            tab["type"] = self.getAttrib(item, "type")
            tab["leader-style"] = self.getAttrib(item, "leader-style")
            tab["leader-text"] = self.getAttrib(item, "leader-text")
            self._tab = tab
            if self._stylename is not None:
                self._styles[self._stylename]["tab"] = tab
            self.tabs.append(tab)
        elif item.tag == "tab":
            style = self.solveStyle(item, self._stylename)
            res += "<span%s>%s</span>" % (style, '&nbsp;' * 9)
            #res += "<tab%s/>%s" % (style, '')
        elif item.tag == "span":
            style = self.solveStyle(item)
            res += "<span%s>" % (style)
            res_close += "</span>"
        elif item.tag == "h":
            level = self.getAttrib(item, "outline-level")
            if level is None:
                level = "1"
            style = self.solveStyle(item)

            self.setupLevel(level)
            lab = self.levelLabel(level)
            self._localtargets[lab] = self.page()
            if item.text is not None:
                lab += item.text
                self._localtargets[lab] = self.page()
            res += '<h%s%s><a name="%s"></a>' % (level, style, lab)
            if level not in self.titles:
                self.titles[level] = []
            self.titles[level].append(item.text)

            res_close += "</h%s>\n" % (level)
        elif item.tag == "p":
            extra = self.solveStyle(item)
            snam = self.getAttrib(item, "style-name")
            if snam is not None:
                pah = ' class="%s"' % (snam)
            else:
                pah = ''
            #if item.text is None or item.text == "":
            #    res += "<div class='emptyline'>&nbsp;</div>\n"
            #else:
            res_start += "<div%s%s>" % (extra, pah)
            res_close += "</div>\n"

        subdata = ''
        for ch in item:
            tmp_b = self.parseTag(ch, page=page)
            if tmp_b:
                subdata += tmp_b

        tmp_f = ''
        if item.tag == 'p' and not subdata and item.text is None:
            res += "<div class='emptyline'>&nbsp;</div>\n"
        else:
            res += res_start
            if item.text is not None:
                res += item.text
            res += subdata

            #if self._page == page:
            #    print self._page, page, tmp
            #res += '%s' % ''.join(tmp_b)

            res += res_close

        if res is not None:
            res += self.handleTail(item)
        if item.tag == "frame":
            self._framedata = None
        elif item.tag == "style":
            self._stylestack.pop()
            if self._stylestack:
                self._stylename = self._stylestack[-1]
            else:
                self._stylename = None
        elif item.tag == "imageframe":
            self._imageframe1 = ''
            self._imageframe1_end = ''
            self._imageframe2 = ''
            self._imageframe2_end = ''
        #elif item.tag == "tab-stop":
        #    self._tab = None

        #print 'res', page, res
        #if page not in self._pagedata:
        #    self._pagedata[page] = ''
        #self._pagedata[page] += res
        #res += '\n<!--end-->\n</div>\n'

        return res

    def getStyle(self, name):
        if name in self._styles:
            return self._styles[name]
        return None

    def page(self):
        return self._page

    def pageCount(self):
        if self._pagecnt is not None:
            return self._pagecnt

        pagecnt = 1
        for item in self._content_root.getiterator():
            if item.tag == "style":
                extra = self.parseStyleTag([item])
                self.mergeStyles(extra)

            if "style-name" in item.attrib:
                st = self.getStyle(item.attrib["style-name"])
                if st is not None and "para-prop" in st:
                    if self.isBreak(st):
                        pagecnt += 1

        self._pagecnt = pagecnt
        return pagecnt

    def read(self):
        if self._read:
            return True
        if not self.open():
            return False

        self._styles_xml = self.extract("styles.xml")
        self._content_xml = self.extract("content.xml")
        self.parseXML()
        self._styles = self.parseStyles()

        self.close()
        return True
