# -*- coding: utf-8 -*-

import sys
import logging
import asyncio
from .utils import UrlFilter

try:
    # Python 3.4.
    from asyncio import JoinableQueue as Queue
except ImportError:
    # Python 3.5.
    from asyncio import Queue

# provide command line support
# import argparse
# ARGS = argparse.ArgumentParser(description="Web crawler")
# ARGS.add_argument(
#     '--config', action='store', dest='config_path',
#     default='./config.json', help='path to load configs'
# )

class Crawler(object):

    """
    a crawler class that takes necessary helpers
    """
    def __init__(self, fetcher, parser, saver, root_urls, loop=None, num_fetchers=10, max_redirect=10):

        self._fetcher = fetcher    # fetcher instance
        self._parser = parser      # parser instance
        self._saver = saver        # saver instance
        
        self._url_filter = UrlFilter()

        self._loop = loop or asyncio.get_event_loop
        self._queue = asyncio.Queue(loop=self._loop)

        self._num_fetchers = num_fetchers
        self._max_redirect = max_redirect

        self._running_tasks = 0

        for url in root_urls:
            self.add_a_task(url, max_redirect)
        return


    def start_work_and_wait(self):
        """
        keep the event loop running until all work finished
        """
        try:
            self._loop.run_until_complete(self._start())
        except KeyboardInterrupt:
            sys.stderr.flush()
            print('\nInterrupted by user\n')
        finally:
            # next two lines are required for actual aiohttp resource cleanup
            self._loop.stop()
            self._loop.run_forever()
            self._loop.close()
        return


    async def _start(self):
        """
        start the tasks, and wait for finishing
        """
        # initialize fetcher session
        self._fetcher.init_session(self._loop)

        # start tasks and wait done
        tasks_list = [asyncio.Task(self._work(index + 1), loop=self._loop)
                      for index in range(self._num_fetchers)]
        await self._queue.join()
        for task in tasks_list:
            task.cancel()

        # close fetcher session
        self._fetcher.close_session()
        return


    async def _work(self, index):
        """
        working process, fetching --> parsing --> saving
        """
        logging.warning("%s[worker-%s] start...", self.__class__.__name__, index)
        self._running_tasks += 1

        while True:
            try:
                # get a task
                url, max_redirect = await self._queue.get()
            except asyncio.CancelledError:
                break

            try:
                # fetch the content of a url
                fetch_result, content = await self._fetcher.fetch(url)
                if fetch_result == 1:

                    # parse the content of a url
                    parse_result, url_list, save_list = await self._parser.parse(url, content)

                    if parse_result == 1:

                        # add new task to self._queue
                        for _url in url_list:
                            self.add_a_task(_url, 0)

                        # save the item of a url
                        for item in save_list:
                            await self._saver.save(url, item)

                    # end of if parse_result > 0
                # TODO: change to be handled inside fetcher
                elif fetch_result == 0:
                    self.add_a_task(url, max_redirect)
                # end of if fetch_result == 1

            # TODO: change to more specific Exception
            except Exception as e:
                logging.error("%s[worker-%s] error: %s", self.__class__.__name__, index, e)
            finally:
                # finish a task
                self._queue.task_done()
                if fetch_result == -2:
                    logging.error(
                        "%s[worker-%s] error: fetch failed and try to stop",
                        self.__class__.__name__, index
                    )
                    break
        # end of while True

        # stop tasks according to self._running_tasks
        self._running_tasks -= 1
        while (not self._running_tasks) and (not self._queue.empty()):
            await self._queue.get()
            self._queue.task_done()

        logging.warning("%s[worker-%s] end...", self.__class__.__name__, index)
        return


    def add_a_task(self, url, max_redirect):
        """
        add a task based on task_name
        """
        # TODO: try to avoid calling check_and_add() in if statement
        if (max_redirect > 0) or (not self._url_filter) or self._url_filter.check_and_add(url):
            self._queue.put_nowait((url, max_redirect))
        return
