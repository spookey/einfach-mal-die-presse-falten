from email.utils import format_datetime
from xml.dom.minidom import getDOMImplementation

from lib.extra import ENCODING


class Generate:
    def __init__(self, conv):
        self.conv = conv
        impl = getDOMImplementation()
        self.dom = impl.createDocument(None, "rss", None)

    def append(self, parent, tag, text=None, data=False, **attrs):
        node = self.dom.createElement(tag)
        if text is not None:
            func = self.dom.createTextNode
            if data:
                func = self.dom.createCDATASection
            node.appendChild(func(text))
        for name, value in attrs.items():
            node.setAttribute(name, value)
        parent.appendChild(node)
        return node

    def items(self):
        for entry in self.conv():
            item = self.dom.createElement("item")
            self.append(item, "title", text=entry["title"], data=True)
            self.append(
                item,
                "guid",
                text=entry["guid"],
                data=False,
                **(
                    {"isPermaLink": "false"}
                    if entry["link"] != entry["guid"]
                    else {}
                ),
            )
            origin = entry["origin"].upper()
            for char in ("_", "/"):
                origin = origin.split(char)[-1]
            self.append(
                item,
                "description",
                text=f"{origin} {entry['description']}",
                data=True,
            )
            for field in ("link", "pubDate"):
                self.append(item, field, text=entry[field], data=False)
            yield item

    def __call__(self, base_url):
        doc = self.dom.documentElement
        doc.setAttribute("version", "2.0")
        chan = self.append(doc, "channel", None)
        self.append(chan, "title", self.conv.args.title)
        self.append(chan, "link", base_url)
        self.append(chan, "description", self.conv.args.desc)
        self.append(chan, "language", self.conv.args.language)
        self.append(chan, "pubDate", format_datetime(self.conv.now))
        for item in self.items():
            chan.appendChild(item)

        feed = doc.toprettyxml(indent="  ", encoding=ENCODING).decode(ENCODING)

        with open(self.conv.args.file, "w", encoding=ENCODING) as handle:
            return handle.write(feed) > 0
