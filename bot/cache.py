import logging
from datetime import datetime, timedelta
from time import sleep

from config import LOG_CACHE

logger = logging.getLogger(__name__)


class Cache:
    def __init__(self):
        self.db = {}
        self._log("Cache initialized.")

    # Adds an entry to the cache.
    def add(self, entry, data, ttl_min, ttl_sec=0):
        if entry in self.db:
            self.db[entry].update(
                {
                    "updated": self._strf(datetime.now()),
                    "data": data,
                    "expires": self._strf(
                        datetime.now() + timedelta(0, ttl_sec, 0, 0, ttl_min)
                    ),
                }
            )
            self._log(f'Entry "{entry}" updated in cache.')
        else:
            self.db[entry] = {
                "created": self._strf(datetime.now()),
                "updated": self._strf(datetime.now()),
                "data": data,
                "expires": self._strf(
                    datetime.now() + timedelta(0, ttl_sec, 0, 0, ttl_min)
                ),
            }
            self._log(f'Entry "{entry}" created in cache.')

    # Removes an entry from the cache.
    def remove(self, entry):
        if entry in self.db:
            self.db.pop(entry)
            self._log(f'Entry "{entry}" removed from cache.')
        else:
            self._log(f'Entry "{entry}" not found.')

    # Flushes the cache.
    def flush(self):
        self.db = {}
        self._log("Cache flushed.")

    # Removes any expired entries in the cache.
    def clean(self):
        expired = []
        for entry in self.db.keys():
            if datetime.now() > self._strp(self.db[entry]["expires"]):
                expired.append(entry)
                self._log(f'Entry "{entry}" found as expired.')
        for entry in expired:
            self.db.pop(entry)
            self._log(f'Entry "{entry}" removed from cache')

    # Gets an entry from the cache.
    def get(self, entry):
        if entry in self.db:
            if datetime.now() > self._strp(self.db[entry]["expires"]):
                self.db.pop(entry)
                self._log(f'Entry "{entry}" found as expired, removed from cache.')
                return None
            return self.db[entry]["data"]
        return None

    # Datetime to string
    def _strf(self, d):
        return d.strftime("%Y-%m-%d %H:%M:%S,%f")

    # String to datetime
    def _strp(self, s):
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S,%f")

    # Logging
    def _log(self, s):
        if LOG_CACHE:
            logger.info(s)


cache = Cache()
