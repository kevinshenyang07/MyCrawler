# -*- coding: utf-8 -*-

import sys
import time
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
        self._stats = {
            'sent_requests': 0,
            'finished_tasks': 0,
            't0': time.time()
        }
        return


    def start_work_and_wait(self):
        """
        keep the event loop running until all work finished
        """
        try:
            self._loop.run_until_complete(self._start())
        except KeyboardInterrupt:
            # sys.stderr.flush()
            print('\nInterrupted by user\n')
            logging.info('statistics: %r', self._stats)
            logging.info('time elapsed: %r seconds', time.time() - self._stats['t0'])
        finally:
            self._fetcher.close_session()
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

        await self._fetcher.queue_join()
        for task in tasks_list:
            task.cancel()
        return


    async def _work(self, index):
        """
        working process, fetching -> parsing -> saving
        """
        logging.warning("%r[worker-%r] start...", self.__class__.__name__, index)
        
        try:
            while True:
                url, redirects, depth = await self._fetcher.get_a_task()
                # fetch the content of a url
                # fetch_result => (response status, url, response_text)
                fetch_status, fetch_result = await self._fetcher.fetch(url, redirects, depth)
                self._stats['sent_requests'] += 1

                # if fetch result is html and not an error page
                if fetch_status == 0 and (fetch_result[0] not in (404, 500)):
                    # parse the content of a url
                    # item => (title, timestamp)
                    parse_status, url_list, item = await self._parser.parse(url, depth, fetch_result[-1])

                    # if parsing successful
                    if parse_status == 0:
                        # add new task to self._queue, use _url to avoid url overwritting
                        for _url in url_list:
                            self._fetcher.add_a_task(_url, 0, depth + 1)
                        # save the item of a url
                        await self._saver.save(url, item)
                        self._stats['finished_tasks'] += 1

        except asyncio.CancelledError as e:
        # except Exception as e:
            logging.error("%r[worker-%r] error: %r", self.__class__.__name__, index, e)
        
        finally:
            self._fetcher.finish_a_task()
        # end of while True

        logging.warning("%r[worker-%r] end...", self.__class__.__name__, index)
        return



