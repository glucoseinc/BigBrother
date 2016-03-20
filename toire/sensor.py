# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import)
import logging
import time

import RPi.GPIO as GPIO

from . import config
from . import ad_convertor


__all__ = ['HCSR04', 'GP2Y0A710K']


logger = logging.getLogger(__name__)

SPEED_OF_SOUND = 340  # [m/s]


class AbstractSensor(object):
    def measure_distance(self):
        raise NotImplementedError

    def clean_up(self):
        raise NotImplementedError


class HCSR04(AbstractSensor):
    def __init__(self):
        super(HCSR04, self).__init__()

        self.trig_pin = config.getint('HC-SR04', 'trig_pin')
        self.echo_pin = config.getint('HC-SR04', 'echo_pin')

        GPIO.setwarnings(False)

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.trig_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)
        GPIO.output(self.trig_pin, GPIO.LOW)
        time.sleep(0.3)

    def measure_distance(self):
        # パルスを10us以上出力
        GPIO.output(self.trig_pin, GPIO.HIGH)
        time.sleep(1.2E-5)
        GPIO.output(self.trig_pin, GPIO.LOW)

        while GPIO.input(self.echo_pin) == GPIO.LOW:
            signal_off = time.time()

        while GPIO.input(self.echo_pin) == GPIO.HIGH:
            signal_on = time.time()

        diff_time = signal_on - signal_off
        # 超音波が反射して戻ってくるまでの時間なので半分にする
        distance = diff_time / 2.0 * SPEED_OF_SOUND
        return distance

    def clean_up(self):
        GPIO.cleanup()


class GP2Y0A710K(AbstractSensor):
    def __init__(self):
        super(GP2Y0A710K, self).__init__()

        self.ad_convertor = getattr(ad_convertor, config.get('GP2Y0A710K', 'ad_convertor'))()

    def measure_distance(self):
        voltage = self.ad_convertor.read()
        logger.debug('voltage: {}'.format(voltage))
        # 距離の逆数特性から距離を計算
        distance = 1 / ((voltage - config.getfloat('GP2Y0A710K', 'intercept')) / config.getfloat('GP2Y0A710K', 'coefficient'))
        return distance

    def clean_up(self):
        self.ad_convertor.clean_up()
