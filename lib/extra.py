from json import loads
from json.decoder import JSONDecodeError
from urllib.error import URLError
from urllib.request import urlopen

ENCODING = 'UTF-8'
FIELDS = (
    'description',
    'guid',
    'link',
    'pubDate',
    'title',
)


def lvz_fetch_full(elem):
    link = elem.get('link', None)
    if not link:
        return None

    try:
        with urlopen(link) as resp:
            html = resp.read().decode(ENCODING)
    except URLError:
        return None
    else:

        for part in [
                elem.split('ld+json">')[-1]
                for elem in
                html.split('</script>') if 'ld+json' in elem
        ]:
            try:
                body = loads(part)
            except JSONDecodeError:
                continue

            text = body.get('articleBody', None)
            if text:
                elem['description'] = text
                return elem

    return None
