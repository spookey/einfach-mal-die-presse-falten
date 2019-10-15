from json import loads
from urllib.request import urlopen

ENCODING = 'UTF-8'
FIELDS = (
    'description',
    'guid',
    'link',
    'pubDate',
    'title',
)


def fp_arg_premium(parser, _help):
    parser.add_argument(
        '-p', '--premium', default='***',
        help=_help('title prefix for premium articles'),
    )


def lvz_fetch_full(elem):
    link = elem.get('link', None)
    if not link:
        return elem

    with urlopen(link) as resp:
        html = resp.read().decode(ENCODING)

        for part in [
                elem.split('ld+json">')[-1]
                for elem in
                html.split('</script>') if 'ld+json' in elem
        ]:
            body = loads(part)
            text = body.get('articleBody', None)
            if text:
                elem['description'] = text
    return elem
