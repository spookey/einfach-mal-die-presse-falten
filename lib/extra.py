from urllib.error import URLError
from urllib.request import urlopen

from bs4 import BeautifulSoup

ENCODING = "UTF-8"
FIELDS = (
    "description",
    "guid",
    "link",
    "pubDate",
    "title",
)


def _fetch_html(elem):
    link = elem.get("link", None)
    if not link:
        return None

    try:
        with urlopen(link) as resp:
            html = resp.read().decode(ENCODING)
    except URLError:
        return None
    return html


def frankenpest_fetch_full(elem):
    html = _fetch_html(elem)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")
    body = soup.select_one("div.brickgroup.body")
    if not body:
        return None

    intro = body.select_one("div.intro-text")
    texts = body.select("div.article-text")
    if not intro or not all(texts):
        return None

    elem["description"] = "<br/>".join(
        elem.text.strip() for elem in (intro, *texts)
    )
    return elem
