import zipfile
import os
import xml.etree.ElementTree as etree
import re

class ODTPage:
    def getPage(self, name="test.odt"):
        odt = ODT(name)
        #res = odt.read()
        return self.getHeader()+self.getBody(odt)+self.getFooter()

    def getHeader(self):
        return """<html>
        <head>
            <title>ODT</title>
            <link rel="stylesheet" type="text/css" title="styles" href="odt.css"/>
            <script type="text/javascript" src="jquery.min.js"></script>
            <script type="text/javascript" src="odt.js"></script>
        </head>
        """
        #<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js"></script>

    def getBody(self, odt):
        res = odt.read()
        if not res:
            cntx = "<p>Invalid file</p>"
        else:
            data = odt.parseStyles()
            odt.parseTextProperties()
            cntx = "<p>Ok: %s</p>" % (data)
        return """
        <body>
            <h1>ODT-HTML5</h1>

            %s
        </body>
"""%(cntx)

    def getFooter(self):
        return """</html>"""

class ODT:
    def __init__(self, name):
        self._name = name
        self._zip = None
        self._styles = {}
        self._styles_xml = None
        self._content_xml = None
        self._stylename = None

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
            res += self.findElement(child, name)
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
        return res

    def filterAttributes(self, datas, keep):
        res = []
        for prop in props:
            style = {}
            for val in prop.attrib:
                if val in valid_text_attrs:
                    style[val] = prop.attrib[val]

            if style:
                res.append(style)

        return res

    def parseTextPropertyTag(self, props):
        valid_text_attrs = ["font-size", "color", "background-color", "font-weight",
            "font-style", "text-underline-style", "text-underline-color",
            "text-overline-style", "text-line-through-style" ]

        return filterAttributes(props, valid_text_attrs)
        
    def parseParagraphPropertyTag(self, props):
        valid_para_attrs = [ "break-before", "text-align", "color", "background-color",
            "text-indent", "margin-left", "margin-right", "margin-top", "margin-bottom" ]
        
        return filterAttributes(props, valid_para_attrs)

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

    def parseXML(self):
        if self._styles_xml == None:
            return None
        self.__root = etree.fromstring(self._styles_xml)
        self.stripNamespace(self.__root)

    def parseParagraphProperties(self):
        tags = self.findElement(self.__root, "paragraph-properties")
        self.parseParagraphPropertyTag(tags)

    def parseTextProperties(self):
        tags = self.findElement(self.__root, "text-properties")
        return self.parseTextPropertyTag(tags)

    def parseStyles(self):
        styles = self.findElement(self.__root, "style")
        return self.parseStyleTag(styles)

        #res += "<p> %s </p>\n"%self.findElement(root, "style")
        #res += "<p> %s </p>\n"%self.findElement(root, "text-properties")
        #res += "<p> %s </p>\n"%self.findElement(root, "paragraph-properties")
        #parser = etree.XMLParser()
        #parser.feed(self._styles)
        #parser.close()

    def read(self):
        if not self.open():
            return False

        self._styles_xml = self.extract("styles.xml")
        self._content_xml = self.extract("content.xml")
        self.parseXML()

        self.close()
        return True
