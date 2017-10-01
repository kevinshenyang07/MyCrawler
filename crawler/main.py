# -*- coding: utf-8 -*-

import asyncio
import logging
import sys
import json

from .insts.inst_fetch

def main():
    with open('./config.json', 'r') as f:
        args = json.load(f)
    if not args['root_urls']:
        print('Add URLs to be parsed in the "root_urls" field of config.json.')
        return 

    levels = [logging.ERROR, logging.WARN, logging.INFO, logging.DEBUG]
    logging.basicConfig(level=levels[min(args['logging_level'], len(levels) - 1)])

    loop = asyncio.get_event_loop()
