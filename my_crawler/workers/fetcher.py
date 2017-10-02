# -*- coding: utf-8 -*-

import random
import logging
import asyncio
import aiohttp
import urllib.parse

from ..utils import UrlFilter, make_random_useragent


class Fetcher(object):
    
    def __init__(self, max_tries=4, sleep_interval=0):
        self._max_tries = max_tries
        self._sleep_interval = sleep_interval
        self._session = None
        self._url_filter = UrlFilter()
    
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

    def _is_redirect(self, response):
        return response.status in (300, 301, 302, 303, 307)

    async def fetch(self, url, max_redirect):
        """
        fetch content of one URL, there are 3 possible outcomes
        1. fetch successful, response is not a redirect (0)
        2. fetch successful, response is a redirect (1)
        3. requests exceed max_tries, no response (-1)
        4. url exexceeds max_redirects, no response (-2)
        :return response_status, content
        """
        logging.debug("%r start: url=%r", self.__class__.__name__, url)

        tries = 0
        exception = None  # for further debugging purpose

        while tries < self._max_tries:
            
            await asyncio.sleep(random.randint(0, self._sleep_interval))

            try:
                response = await self._session.get(
                    url, allow_redirect=False, timeout=5
                )  # aiohttp follows redirects by default
                if tries > 1:
                    logging.info("success on %r time fetching %r", tries, url)
                break
            
            except aiohttp.ClientError as client_error:
                logging.info('try %r for %r raised %r', tries, url, client_error)
                exception = client_error
                tries += 1
        # end of while loop

        if tries > self._max_tries:
            logging.error('%r failed after %r tries', url, self._max_tries)
            return -1, None

        # why using try here?
        try:
            if self._is_redirect(response):
                location = response.headers['location']
                next_url = urllib.parse.urljoin(url, location)
                
                if max_redirect > 0:
                    is_new_url = self._url_filter.check_and_add(next_url)
                    if is_new_url:
                        logging.info('redirect to %r from %r', next_url, url)
                        status = 1
                        content = (next_url, max_redirect - 1)
                else:
                    logging.error('redirect limit reached for %r from %r',
                                next_url, url)
                    status = -2
                    content = None
            else:
                status = 0
                content = (response.status, response.url, await response.text())
        finally:
            await response.release()

        logging.debug("%r end: fetch_status=%r, url=%r",
                      self.__class__.__name__, status, url)
        return status, content
