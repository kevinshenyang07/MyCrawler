# -*- coding: utf-8 -*-

import re
from pybloom_live import ScalableBloomFilter
from .util_config import CONFIG_URL_FILTER_PATTERN


class UrlFilter(object):
    """
    class of UrlFilter, to filter url by regexs and (bloomfilter or set)
    """

    def __init__(
            self, 
            black_patterns=(CONFIG_URL_FILTER_PATTERN,), 
            white_patterns=(r"^http",), 
            capacity=None):
        
        """
        constructor, use variable of BloomFilter if capacity else variable of set
        """
        self._re_black_list = [re.compile(pattern, flags=re.IGNORECASE)
                                  for pattern in black_patterns] 
                              if black_patterns else []
        self._re_white_list = [re.compile(pattern, flags=re.IGNORECASE)
                                  for pattern in white_patterns] 
                              if white_patterns else []

        # bloom filter share the same interface with set()
        self._url_set = ScalableBloomFilter(capacity, error_rate=0.001) if capacity else set()
        return

    def check(self, url):
        """
        check the url based on self._re_black_list and self._re_white_list
        """
        # if url in black_list, return False
        for re_black in self._re_black_list:
            if re_black.search(url):
                return False

        # if url in white_list, return True
        for re_white in self._re_white_list:
            if re_white.search(url):
                return True

        # if url not in either list, depend on if white list exists
        return False if self._re_white_list else True

    def check_and_add(self, url):
        """
        check the url to make sure that the url hasn't been fetched, and add url to urlfilter
        """
        is_new_url = False
        if self.check(url):
            is_new_url = url not in self._url_set
            self._url_set.add(url)
        return is_new_url
