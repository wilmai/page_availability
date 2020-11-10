#!/usr/bin/env python

from setuptools import setup

setup(
    name='page_availability',
    version='1.0',
    #description='',
    #author='',
    #author_email='',
    #url='',
    packages=['page_availability'],
    install_requires=[
        'mypy',
        'pytest',
        'pyyaml',
        'aiohttp<4.0', # latest version isn't quite prod ready
        'kafka-python',
        'psycopg2',
    ],
)
