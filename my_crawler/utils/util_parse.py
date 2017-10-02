# -*- coding: utf-8 -*-

import urllib.parse


__all__ = [
    "get_url_legal",
]


def get_url_legal(base_url, url, encoding=None, remove_fragment=True):
    """
    get a legal url from a url, based on base_url, and set url_frags.fragment = "" if remove_fragment is True
    example: http://stats.nba.com/player/#!/201566/?p=russell-westbrook
    """
    url_join = urllib.parse.urljoin(base_url, url, allow_fragments=True)
    url_legal = urllib.parse.quote(
        url_join, safe="%/:=&?~#+!$,;'@()*[]|", encoding=encoding)
    if remove_fragment:
        url_frags = urllib.parse.urlparse(url_legal, allow_fragments=True)
        url_legal = urllib.parse.urlunparse(
            (url_frags.scheme, url_frags.netloc, url_frags.path, url_frags.params, url_frags.query, ""))
    return url_legal
