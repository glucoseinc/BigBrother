# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import)
from periphery import SPI

from . import config


__all__ = ['MCP3208']


class MCP3208(object):
    MAX_CLOCK_SPEED = 2E+6
    RESOLUTION = 0b1 << 12
    SECOND_WORD_MASK = 0b00001111

    def __init__(self):
        self.spi = SPI(
            config.get('MCP3208', 'device_file'),
            0,
            MCP3208.MAX_CLOCK_SPEED
        )
        self.Vref = config.getfloat('MCP3208', 'vref')

    def read(self):
        mosi_data = self._make_mosi_data()
        miso_data = self.spi.transfer(mosi_data)
        _, second_word, third_word = miso_data
        value = ((MCP3208.SECOND_WORD_MASK & second_word) << 8) + third_word
        return value * self.Vref / MCP3208.RESOLUTION

    def clean_up(self):
        self.spi.close()

    def _make_mosi_data(self):
        ch = config.getint('MCP3208', 'ch')
        raw_data = 0b0000011000 + ch
        first_word = (0b11100 & raw_data) >> 2
        second_word = (0b11 & raw_data) << 6
        return [first_word, second_word, 0b0]
