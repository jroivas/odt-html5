import zipfile
import os
import xml.etree.ElementTree as etree
import re

class ODTPage:
    def getPage(self, name="test.odt", page=1):
        odt = ODT(name)
        #res = odt.read()
        pages = odt.pageCount()
        if page > pages:
            page = pages
        if page < 1:
            page = 1
        styles = self.getStyles(pages, page)
        res = self.getHeader(styles) + self.getBody(odt, page) + self.getFooter()
        return res

    def getStyles(self, pagecnt, curpage=1):
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
            

    def getHeader(self, extra=""):
        return """<html>
        <head>
            <title>ODT</title>
            <link rel="stylesheet" type="text/css" title="styles" href="odt.css"/>
            <script type="text/javascript" src="jquery.min.js"></script>
            <script type="text/javascript" src="odt.js"></script>
            %s
        </head>
        """ % (extra)
        #<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js"></script>

    def getBody(self, odt, page):
        res = odt.read()
        if not res:
            cntx = "<p>Invalid file</p>"
        else:
            #data = odt.parseStyles()
            #cntx = "<p>styles: %s</p>" % (data)
            #cntx = "%s" % odt.pageCount()
            tmp = odt.parseContent()
            cntx = """<!-- PREV --><div id='prevPage' onClick='toPrevPage();'>&lt;&lt;</div>
        <input type='hidden' id='pagenum' name='pagenum' value='%s'></input>
        <input type='hidden' id='pagecnt' name='pagecnt' value='%s'></input>

        <!-- START --><div id='pageDiv'>
        <div id='pageNum1' class='pageNum1'>
        %s
        </div>
        <!-- END --></div>

        <!-- NEXT --><div id='nextPage' onClick='toNextPage();'>&gt;&gt;</div>
        """ % (page, odt.pageCount(), tmp)

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
        return self._zip.read(file)

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

    def parseContent(self):
        return self.parseTag(self._content_root)
        res = ""
        for item in self._content_root.getiterator():
            res += "<p>%s %s</p>\n" % (item.tag, item.text)
        return res

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
        return intlink

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

    def solveStyle(self, item):
        combined = {}
        style = self.getAttrib(item, "style-name")
        styledata = self.getStyle(style)
            
        extra = ""
        if styledata is not None:
            cstyledata = styledata

            # Solve style stack
            stack = [styledata]
            while cstyledata is not None and "parent" in cstyledata:
                parstyle = cstyledata["parent"]
                pardata = self.getStyle(parstyle)
                if pardata is not None:
                    stack.append(pardata)
                cstyledata = pardata
            solved_style = {}
            while stack:
                solved_style.update(stack.pop())

            parsedstyle = self.parseStyle(solved_style)
            if parsedstyle:
                extra = ' style="%s"' % (parsedstyle)
        return extra

    def handleTail(self, item):
        if item.tail is not None:
            return item.tail
        return ""

    def parseTag(self, item):
        listname = None
        res = ""
        res_close = ""

        style = self.getAttrib(item, "style-name")
        styledata = self.getStyle(style)
        if self.isBreak(styledata):
            self._page += 1
            res += "</div>\n"
            res += '<div class="pageNum%s" id="pageNum%s">\n' % (self._page, self._page)

        if item.tag == "list-style":
            listname = self.getAttrib(item, "name")
            if not listname in self._lists:
                self._lists[listname] = {}
        elif item.tag == "list-level-style-bullet":
            bullet = self.getAttrib(item, "name")
            if listname is not None:
                self._lists[listname]["bullet"] = bullet
        elif item.tag == "style":
            stylename = self.getAttrib(item, "name")
            parentname = self.getAttrib(item, "parent-style-name")
        elif item.tag == "list":
            style = self.getAttrib(item, "style-name")
            if style is not None and style in self._lists and "bullet" in self._lists[style]:
                res += "<ul>"
                res_close += "</ul>" + self.handleTail(item)
            else:
                res += "<ol>"
                res_close += "</ol>" + self.handleTail(item)
        elif item.tag == "a":
            href = self.getAttrib(item, "href")
            if href is not None:
                extra = self.solveStyle(item)
                res += '<a href="%s"%s>' % (self.parseLink(href), extra)
                res_close += "</a>" + self.handleTail(item)
        elif item.tag == "frame":
            frame = {}
            frame["style"] = self.solveStyle(item)
            frame["anchor"] = self.getAttrib(item, "anchor")
            frame["width"] = self.getAttrib(item, "width")
            frame["height"] = self.getAttrib(item, "height")
            self._framedata = frame
        elif item.tag == "image":
            href = self.getAttrib(item, "href")
            if href is not None:
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
                        imgextra = ' style="%s"' % (img_styles)
                    extra = ""
                    if p_styles:
                        extra = ' style="%s"' % (p_styles)

                    src = "/img/%s" % (href)
                    imgdata = '<img src="%s"%s></img>' % (src, imgextra)
                    if _anchor == "as-is":
                        res += '<span%s>%s</span>' % (extra, imgdata)
                    else:
                        res += '<div%s>%s</div>' % (extra, imgdata)

        elif item.tag == "tab":
            res += "&nbsp;&nbsp;"
        elif item.tag == "span":
            style = self.solveStyle(item)
            res += "<span%s>" % (style)
            res_close += "</span>" + self.handleTail(item)
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
            res_close += "</h%s>\n" % (level) + self.handleTail(item)
            
        elif item.tag == "p":
            extra = self.solveStyle(item)
            if item.text is None or item.text == "":
                res += "<div class='emptyline'>&nbsp;</div>\n" + self.handleTail(item)
            else:
                res += "<div%s>" % (extra)
                res_close += "</div>\n" + self.handleTail(item)
            

        if item.text is not None:
            res += item.text

        for ch in item:
            res += self.parseTag(ch)

        res += res_close
        if item.tag == "frame":
            self._framedata = None

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
                self._styles.update(extra)
                
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
