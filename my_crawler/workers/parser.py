# -*- coding: utf-8 -*-

import re
import logging
import datetime
from ..utilities import get_url_legal


class Parser(object):

    def __init__(self, max_depth=-1):
        self._max_depth = max_depth  # no depth if set to -1 
        return

    async def parse(self, url, depth, content):
        """
        entrance function of Parser
        :return (status, url_list, item):
        """
        logging.debug("%s start: url=%r, depth=%r", self.__class__.__name__, url, depth)

        status, url_list = 0, []

        try:
            html_text = content[-1]

            if self._max_depth < 0 or depth < self._max_depth:
                
                # find all href in the page
                href_list = re.findall(
                    r"<a[\w\W]+?href=\"(?P<url>[\w\W]{5,}?)\"[\w\W]*?>[\w\W]+?</a>",
                    html_text, flags=re.IGNORECASE)

                url_list = [get_url_legal(url, href) for href in href_list]]

            item = self.construct_item(html_next)

        # TODO: substitute to more specific exception
        except Exception as e:
            parse_result, url_list, item = -1, [], (,)
            logging.error("%r error: %r, url=%r, depth=%r",
                          self.__class__.__name__, e, url, depth)

        logging.debug("%r end: status=%r, url=%s, found %r URLs",
                      self.__class__.__name__, status, url, len(url_list))

        return status, url_list, item


    def construct_item(self, html_text):
        """
        based on the fields needed, return the corresponding data
        """
        # find the title of the page
        title = re.search(
            r"<title>(?P<title>[\w\W]+?)</title>", 
            html_text, flags=re.IGNORECASE)

        title = title.group("title").strip()
        timestamp = datetime.datetime.now()

        return (title, timestamp)
