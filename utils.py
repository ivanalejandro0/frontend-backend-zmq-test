#!/usr/bin/env python
# encoding: utf-8
import logging


def get_log_handler(name):
    level = logging.DEBUG
    # level = logging.WARNING

    # Create logger and formatter
    logger = logging.getLogger(name)
    logger.setLevel(level)
    # levelname length == 8, since 'CRITICAL' is the longest
    log_format = ('%(asctime)s - %(levelname)-8s - '
                  'L#%(lineno)-4s : %(name)s:%(funcName)s() - %(message)s')
    formatter = logging.Formatter(log_format)

    # Console handler
    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(formatter)
    logger.addHandler(console)
    logger.debug('Console handler plugged!')

    return logger
