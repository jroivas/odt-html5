import zipfile
import os
import xml.etree.ElementTree as etree

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
            cntx = "<p>Ok: %s</p>"%(data)
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

    def parseStyles(self):
        if self._styles == None:
            return None
        root = etree.fromstring(self._styles)
        res = " %s "%root.tag
        for child in root:
            res += " %s "%(child.tag)
        return res
        #parser = etree.XMLParser()
        #parser.feed(self._styles)
        #parser.close()

    def read(self):
        if not self.open():
            return False

        self._styles = self.extract("styles.xml")
        self._content = self.extract("content.xml")

        self.close()
        return True
