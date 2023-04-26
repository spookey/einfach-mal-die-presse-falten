from datetime import datetime, timedelta
from json import dump, load
from os import path

from lib.extra import ENCODING, FIELDS
from lib.fetch import Fetch


class Convert:
    def __init__(self, args, feed_input, encoding=ENCODING, extra=None):
        self.args = args
        self.feed_input = feed_input
        self.encoding = encoding
        self.extra = extra
        self.now = datetime.utcnow()

    def _read(self):
        if path.exists(self.args.cache):
            with open(self.args.cache, "r", encoding=ENCODING) as handle:
                return load(handle)
        return []

    @staticmethod
    def epoch(time):
        return int((time - datetime.utcfromtimestamp(0)).total_seconds())

    def limited_ordered(self, cache):
        limit = self.epoch(self.now - timedelta(days=self.args.keep))
        return sorted(
            (elem for elem in cache if elem["time"] >= limit),
            key=lambda el: el["time"],
            reverse=True,
        )

    def _write(self, cache):
        with open(self.args.cache, "w", encoding=ENCODING) as handle:
            dump(cache, handle, indent=2)
        return cache

    def pull(self, feed_input):
        time = self.epoch(self.now)
        for entry in [
            fl
            for at in (
                Fetch(name, url, encoding=self.encoding)()
                for name, url in feed_input.items()
                if name not in self.args.excludes
            )
            for fl in at
        ]:
            entry["time"] = time
            if self.extra:
                entry = self.extra(entry)
            if entry:
                yield entry

    @staticmethod
    def valuable(cache, entry):
        for item in cache:
            for field in FIELDS:
                value = entry.get(field, None)
                if not value:
                    return False
                if item.get(field, None) == value:
                    return False
        return True

    def __call__(self):
        cache = self._read()
        for entry in self.pull(self.feed_input):
            if self.valuable(cache, entry):
                cache.append(entry)
        return self._write(self.limited_ordered(cache))
