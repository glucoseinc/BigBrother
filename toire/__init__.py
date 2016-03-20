# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import)
import ConfigParser
import logging
import os


config = ConfigParser.ConfigParser()
with open(os.path.join(os.path.dirname(__file__), '..', 'toire.cfg'), 'r') as cfg:
    config.readfp(cfg)


logging.basicConfig(
    level=logging.DEBUG if config.getboolean('mode', 'debug') else logging.INFO,
    format='[%(asctime)s] %(name)s - %(levelname)s - %(message)s'
)
