# -*- coding: utf-8 -*-

"""
install script: python3 setup.py install
"""

from setuptools import setup, find_packages

setup(
    name="mycrawler",
    version="0.0.1",
    author="kevinshenyang07",
    keywords=["crawler", "asyncio", "distributed"], 
    packages=find_packages(exclude=("test.*",)),
    package_data={
        "": ["*.conf"],         # include all *.conf files
    },
    install_requires=[
        "aiohttp>=2.2.0",       # aiohttp, http for asyncio
        "pybloom_live>=2.2.0",  # pybloom-live, fork from pybloom
        "redis>=2.10.0",        # redis, python client for redis
    ]
)
