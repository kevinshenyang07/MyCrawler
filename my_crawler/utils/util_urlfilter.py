# -*- coding: utf-8 -*-

import re
from .util_config import CONFIG_URL_FILTER_PATTERN


class UrlFilter(object):
    """
    class of UrlFilter, to filter url by regexs and (bloomfilter or set)
    """

    def __init__(self, black_patterns=(CONFIG_URL_FILTER_PATTERN,), 
                 white_patterns=(r"^http[s]{0,1}://",), capacity=None):
        """
        constructor, use variable of BloomFilter if capacity else variable of set
        """
        self._re_black_list = [re.compile(pattern, flags=re.IGNORECASE) \
                                  for pattern in black_patterns] \
                              if black_patterns else []
        self._re_white_list = [re.compile(pattern, flags=re.IGNORECASE) \
                                  for pattern in white_patterns] \
                              if white_patterns else []

        # bloom filter share the same interface with set()
        if capacity:
            from pybloom_live import ScalableBloomFilter
            self._url_set = ScalableBloomFilter(capacity, error_rate=0.001)
        else:
            self._url_set = set()
        return

    def should_add(self, url):
        """
        check if a url should be added to URL queue
        based on black list, white list and if that url in set
        """
        # if url in any pattern of black_list, return False
        for re_black in self._re_black_list:
            if re_black.search(url):
                return False

        # if url in any pattern of white_list, do further check
        for re_white in self._re_white_list:
            if re_white.search(url) and (url not in self._url_set):
                return True

        # if no patterns in white list match url, then return False
        return False

    def add(self, url):
        """
        simply add url to set
        """
        self._url_set.add(url)
