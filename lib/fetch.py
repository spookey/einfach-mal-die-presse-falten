from html import unescape
from urllib.error import HTTPError
from urllib.request import urlopen
from xml.dom.minidom import parseString
from xml.parsers.expat import ExpatError  # pylint: disable=no-name-in-module

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
            try:
                with urlopen(self.url) as resp:
                    doc = resp.read().decode(self.encoding)
                    if doc:
                        self._doc = parseString(doc)

            except (HTTPError, ExpatError):
                return None

        return self._doc

    @staticmethod
    def entry(item):
        for elem in item.childNodes:
            if elem.nodeName in FIELDS:
                elem.normalize()
                content = unescape(
                    elem.firstChild.data if elem.hasChildNodes() else elem.data
                ).strip()
                if content:
                    yield (elem.nodeName, content)

    def __call__(self):
        if self.doc is None:
            return

        for item in self.doc.getElementsByTagName('item'):
            result = {'origin': self.name}
            result.update(self.entry(item))
            yield result
