from html import unescape
from urllib.request import urlopen
from xml.dom.minidom import parseString

from lib.extra import FIELDS


class Fetch:
    def __init__(self, name, url, encoding):
        self.name = name
        self.url = url
        self.encoding = encoding
        self._doc = None

    @property
    def doc(self):
        if self._doc is None:
            with urlopen(self.url) as resp:
                doc = resp.read().decode(self.encoding)
                self._doc = parseString(doc)
        return self._doc

    @staticmethod
    def entry(item):
        for elem in item.childNodes:
            elem.normalize()
            content = unescape(
                elem.firstChild.data if elem.hasChildNodes() else elem.data
            )
            if content and elem.nodeName in FIELDS:
                yield (elem.nodeName, content)

    def __call__(self):
        for item in self.doc.getElementsByTagName('item'):
            result = {'origin': self.name}
            result.update(self.entry(item))
            yield result
