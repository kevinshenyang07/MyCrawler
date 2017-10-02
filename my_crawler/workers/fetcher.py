# -*- coding: utf-8 -*-

import random
import logging
import asyncio
import aiohttp
import urllib.parse
from ..utils import make_random_useragent


class Fetcher(object):
    
    def __init__(self, max_tries=4, sleep_interval=0):
        self._max_tries = max_tries
        self._sleep_interval = sleep_interval
        self._session = None
    
    def init_session(self, loop):
        """
        initialize a session based on exisiting loop
        """
        if not self._session:
            headers = {"User-Agent": make_random_useragent(),
                       "Accept-Encoding": "gzip"}
            self._session = aiohttp.ClientSession(loop=loop, headers=headers)
        return 

    def close_session(self):
        if not self._session.closed:
            self._session.close()
        return 

    def _is_redirect(response):
        return response.status in (300, 301, 302, 303, 307)


    async def fetch(self, url, max_redirect):
        """
        fetch content of one URL
        :return is_successful, content
        """
        logging.debug("%s start: url=%s", self.__class__.__name__, url)

        tries = 0
        exception = None

        while tries < self._max_tries:
            
            await asyncio.sleep(random.randint(0, self._sleep_time))

            try:
                response = await self._session.get(
                    url, allow_redirect=False, timeout=5
                )
                if tries > 1:
                    logging.info("success on %i time fetching %s", tries, url)
                break
            
            except aiohttp.ClientError as client_error:
                LOGGER.info('try %r for %r raised %r', tries, url, client_error)
                exception = client_error

            tries += 1
            
        
        

            fetch_result, content = 1, (response.status, response.url, await response.text())
            await response.release()

        except aiohttp.ClientError as client_error:
            if repeat >= self._max_repeat:
                fetch_result, content = -1, None
                logging.error("%s error: %s, keys=%s, repeat=%s, url=%s",
                              self.__class__.__name__, excep, keys, repeat, url)
            else:
                fetch_result, content = 0, None
                logging.debug("%s repeat: %s, keys=%s, repeat=%s, url=%s",
                              self.__class__.__name__, excep, keys, repeat, url)

        logging.debug("%s end: fetch_result=%s, url=%s",
                      self.__class__.__name__, fetch_result, url)
        return fetch_result, content


    def handle_redirect(response):
        location = response.headers['location']
        next_url = urllib.parse.urljoin(url, location)

        if next_url in self.seen_urls:
            return
        if max_redirect > 0:
            LOGGER.info('redirect to %r from %r', next_url, url)
            self.add_url(next_url, max_redirect - 1)
        else:
            LOGGER.error('redirect limit reached for %r from %r',
                            next_url, url)
