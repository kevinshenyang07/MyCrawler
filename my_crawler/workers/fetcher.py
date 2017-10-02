# -*- coding: utf-8 -*-

import random
import logging
import asyncio
import aiohttp
import urllib.parse

try:
    # Python 3.4.
    from asyncio import JoinableQueue as Queue
except ImportError:
    # Python 3.5.
    from asyncio import Queue

from ..utils import UrlFilter, make_random_useragent, is_redirect


class Fetcher(object):
    
    def __init__(self, loop, root_urls, max_tries=4, max_redirects=10, sleep_interval=0):
        self._loop = loop
        self._root_urls = root_urls
        self._max_tries = max_tries
        self._max_redirects = max_redirects
        self._sleep_interval = sleep_interval

        self._session = None
        self._url_queue = None
        self._url_filter = UrlFilter()

    def init_session(self):
        """
        initialize a session based on exisiting loop
        """
        if not self._session:
            headers = {"User-Agent": make_random_useragent(),
                       "Accept-Encoding": "gzip"}
            self._session = aiohttp.ClientSession(loop=self._loop, headers=headers)
        return 

    def close_session(self):
        if not self._session.closed:
            self._session.close()
        return

    async def init_url_queue(self):
        """
        initialize an async queue and add root urls to the queue
        closing of queue depends on its internal counter of tasks
        """
        self._url_queue = Queue(loop=self._loop)
        # add root URLs to URL queue
        for url in self._root_urls:
            self.add_a_task(url, 0)
        # block until task_done() is called
        await self._url_queue.join()  
        return


    async def fetch(self, url, redirects):
        """
        fetch content of one URL, there are 3 possible outcomes
        1. fetch successful, response is not a redirect (0)
        2. fetch successful, response is a redirect (1)
        3. requests exceed max_tries, no response (-1)
        :return status, result
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

        # when it's not an error response
        return self._handle_response(response)


    def _handle_response(self, response):
        """
        take a non-error response and returns its content
        """
        status, result = 0, None
        try:
            if is_redirect(response):
                location = response.headers['location']
                next_url = urllib.parse.urljoin(url, location)

                if redirects <= self._max_redirects:
                    if self._url_filter.should_add(next_url):
                        self._url_filter.add(next_url)
                        self.add_a_task(url, redirects + 1)
                        logging.info('redirect to %r from %r', next_url, url)
                else:
                    logging.error('redirect limit reached for %r from %r',
                                  next_url, url)
                status = 1
            else:
                result = (response.status, response.url, await response.text())
        finally:
            await response.release()
        
        return status, result


    def add_a_task(self, url, redirects):
        """
        add a (url, redirects) pair to URL queue
        'task' is a conventional term of item for async queue
        """
        if redirects <= self._max_redirects and self._url_filter.should_add(url):
            self._url_queue.put_nowait((url, redirects))
        return

    async def get_a_task(self):
        """
        get a (url, redirects) pair from URL queue
        """
        return await self._url_queue.get() 

    def finish_a_task(self):
        """
        notify a queue one task is done
        """
        self._url_queue.task_done()
        return
