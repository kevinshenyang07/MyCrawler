# -*- coding: utf-8 -*-

import sys
import json
import logging
import asyncio
from my_crawler import Fetcher, Parser, Saver, Crawler


def test_crawler(config_path):

    # load configs, set up logging, get loop
    with open(config_path, 'r') as f:
        configs = json.load(f)
    
    if not configs['root_urls']:
        print('add URLs to be parsed in the "root_urls" field of config.json')
        return

    levels = [logging.ERROR, logging.WARN, logging.INFO, logging.DEBUG]
    logging.basicConfig(
        level=levels[min(configs['logging_level'], len(levels) - 1)])

    loop = asyncio.get_event_loop()

    # initialize fetcher, parser and saver, get crawler ready
    fetcher = Fetcher(
        loop=loop,
        root_urls=configs['root_urls'],
        max_tries=configs['max_tries'], 
        max_redirect=configs['max_redirect'],
        sleep_interval=configs['sleep_interval']
    )
    parser = Parser(max_depth=configs['max_depth'])
    saver = Saver(save_pipe=open("my_crawler_output.txt", "w"))

    crawler = Crawler(
        fetcher, parser, saver, loop=loop,
        num_tasks=configs['num_tasks']
    )

    crawler.start_work_and_wait()


if __name__ == '__main__':
    test_crawler('./config.json')
    exit()
