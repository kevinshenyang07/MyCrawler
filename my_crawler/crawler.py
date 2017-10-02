# -*- coding: utf-8 -*-

import sys
import logging
import asyncio

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
    def __init__(self, fetcher, parser, saver, loop=None, num_tasks=10):

        self._fetcher = fetcher    # fetcher instance
        self._parser = parser      # parser instance
        self._saver = saver        # saver instance
        
        self._loop = loop or asyncio.get_event_loop

        self._num_tasks = num_tasks
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
        self._fetcher.init_session()

        # start tasks and wait done
        tasks_list = [asyncio.Task(self._work(index + 1), loop=self._loop)
                      for index in range(self._num_tasks)]

        self._fetcher.init_url_queue(self._loop)
        for task in tasks_list:
            task.cancel()

        # close fetcher session
        self._fetcher.close_session()
        return


    async def _work(self, index):
        """
        working process, fetching -> parsing -> saving
        """
        logging.warning("%r[worker-%r] start...", self.__class__.__name__, index)

        while True:
            try:
                url, redirects, depth = await self._fetcher.get_a_task()
                
                # fetch the content of a url
                status, fetch_result = await self._fetcher.fetch(url, redirects, depth)
                
                # if fetch result is html
                if status == 0:
                    # parse the content of a url
                    parse_result, url_list, item = await self._parser.parse(url, fetch_result)

                    if parse_result == 1:

                        # add new task to self._queue
                        for url in url_list:
                            self._fetcher.add_a_task(url, 0, depth + 1)

                        # save the item of a url
                        for item in save_list:
                            await self._saver.save(url, item)
                
                self._fetcher.finish_a_task()

            except asyncio.CancelledError as e:
                logging.error("%r[worker-%r] error: %r", self.__class__.__name__, index, e)
        # end of while True

        logging.warning("%r[worker-%r] end...", self.__class__.__name__, index)
        return



