# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import)
import httplib
import json
import logging
import time
from urlparse import urlparse

from . import config
from . import sensor


__all__ = ['Watcher']


WALL_TO_WALL = config.getfloat('measurement', 'wall_to_wall')
MEASUREMENT_ERROR = config.getfloat('measurement', 'error')
MEASUREMENT_INTERVAL = config.getfloat('measurement', 'interval')
DEBUG = config.getboolean('mode', 'debug')

logger = logging.getLogger(__name__)


class Watcher(object):
    def __init__(self):
        self.sensor_device = getattr(sensor, config.get('sensor', 'name'))()

    def run(self):
        try:
            previous_state = False
            current_state = False
            while True:
                distance = self.sensor_device.measure_distance()
                logger.info('distance: {:0.3f}m'.format(distance))
                current_state = self.is_someone_using(distance)
                if current_state != previous_state:
                    self.notify(current_state)
                previous_state = current_state

                time.sleep(MEASUREMENT_INTERVAL)
        except KeyboardInterrupt:
            logger.info('QUIT')
        except Exception as e:
            logger.error(e)
        finally:
            self.sensor_device.clean_up()

    def is_someone_using(self, distance):
        if WALL_TO_WALL - MEASUREMENT_ERROR < distance:
            return False
        return True

    def notify(self, is_using):
        headers = {'Content-Type': 'application/json'}
        payload = json.dumps({
            'channel': config.get('slack', 'channel'),
            'username': 'トイレ速報',
            'attachments': [{
                'fallback': 'トイレの状態が変わりました。',
                'color': 'danger' if is_using else 'good',
                'fields': [{
                    'title': 'State',
                    'value': '入ってます...' if is_using else '終わりました !',
                }],
            }]
        })
        logger.debug('payload {}'.format(payload))
        if DEBUG:
            return

        parse_result = urlparse(config.get('slack', 'hook_url'))
        connection = httplib.HTTPSConnection(parse_result.netloc)
        connection.request('POST', parse_result.path, payload, headers)
        response = connection.getresponse()
        if response.status != 200:
            logger.error('POST failed: {}'.format(response.reason))
