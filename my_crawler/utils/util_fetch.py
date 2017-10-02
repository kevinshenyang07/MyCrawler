# -*- coding: utf-8 -*-

import random
from .util_config import CONFIG_USERAGENT_PC, CONFIG_USERAGENT_PHONE, CONFIG_USERAGENT_ALL

__all__ = [
    "make_random_useragent",
    "is_redirect"
]


def make_random_useragent(ua_type="all"):
    """
    make a random user_agent based on ua_type, ua_type can be "pc", "phone" or "all"(default)
    """
    ua_type = ua_type.lower()
    assert ua_type in (
        "pc", "phone", "all"), "make_random_useragent: parameter ua_type[%s] is invalid" % ua_type
    return random.choice(CONFIG_USERAGENT_PC if ua_type == "pc" else CONFIG_USERAGENT_PHONE if ua_type == "phone" else CONFIG_USERAGENT_ALL)


def is_redirect(response):
    return response.status in (300, 301, 302, 303, 307)
