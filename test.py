# -*- coding: utf-8 -*-

import sys
import json
import logging
import asyncio
from crawler import Fetcher, Parser, Saver, Crawler


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
    fetcher = Fetcher(max_repeat=3, sleep_time=0)
    parser = Parser(max_deep=-1)
    saver = Saver(save_pipe=open("my_crawler_output.txt", "w"))

    crawler = Crawler(
        fetcher, parser, saver, url_filter=None, loop=loop, num_fetchers=configs['max_fetchers']
    )



if __name__ == '__main__':
    test_crawler('./config.json')
    exit()
