# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import)
import ConfigParser
import httplib
import json
import logging
import os
import time
from urlparse import urlparse

import RPi.GPIO as GPIO


config = ConfigParser.ConfigParser()
with open(os.path.join(os.path.dirname(__file__), '..', 'toire.cfg'), 'r') as cfg:
    config.readfp(cfg)


logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(logging.Formatter('[%(asctime)s] %(name)s - %(levelname)s - %(message)s'))
logger.setLevel(logging.INFO)
logger.addHandler(stream_handler)


TRIG_PIN = config.getint('HC-SR04', 'trig_pin')
ECHO_PIN = config.getint('HC-SR04', 'echo_pin')
SPEED_OF_SOUND = 340  # [m/s]
MIRROR_TO_WALL = config.getfloat('measurement', 'mirror_to_wall')
ERROR = config.getfloat('measurement', 'error')
DEBUG = config.getboolean('mode', 'debug')


def initialize():
    GPIO.setwarnings(False)

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TRIG_PIN, GPIO.OUT)
    GPIO.setup(ECHO_PIN, GPIO.IN)
    GPIO.output(TRIG_PIN, GPIO.LOW)
    time.sleep(0.3)


def measure_distance():
    # パルスを10us以上出力
    GPIO.output(TRIG_PIN, GPIO.HIGH)
    time.sleep(1.2E-5)
    GPIO.output(TRIG_PIN, GPIO.LOW)

    while GPIO.input(ECHO_PIN) == GPIO.LOW:
        signal_off = time.time()

    while GPIO.input(ECHO_PIN) == GPIO.HIGH:
        signal_on = time.time()

    diff_time = signal_on - signal_off
    # 超音波が反射して戻ってくるまでの時間なので半分にする
    return diff_time / 2.0 * SPEED_OF_SOUND


def is_someone_using(distance):
    if MIRROR_TO_WALL - ERROR < distance:
        return False
    return True


def notify(is_using):
    if DEBUG:
        return

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
    parse_result = urlparse(config.get('slack', 'hook_url'))
    connection = httplib.HTTPSConnection(parse_result.netloc)
    connection.request('POST', parse_result.path, payload, headers)
    response = connection.getresponse()
    if response.status == 200:
        logger.error('POST failed: {}'.format(response.reason))


def main():
    try:
        current_state = False
        previous_state = False
        initialize()
        while True:
            distance = measure_distance()
            logger.info('distance: {:0.3f}m'.format(distance))
            current_state = is_someone_using(distance)
            if current_state != previous_state:
                notify(current_state)
            previous_state = current_state

            time.sleep(config.getint('measurement', 'interval'))
    except KeyboardInterrupt:
        logger.info('QUIT')
    finally:
        GPIO.cleanup()


if __name__ == '__main__':
    main()
