#!/usr/bin/env python
# encoding: utf-8
"""
Backend available API and SIGNALS definition.
"""

STOP_REQUEST = "stop"
PING_REQUEST = "PING"

API = (
    STOP_REQUEST,  # this method needs to be defined in order to support the
                   # backend stop action
    PING_REQUEST,
    "add",
    "reset",
    "get_stored_data",
    "blocking_method",

    'twice_01',
    'twice_02',
)


SIGNALS = (
    "add_result",
    "reset_ok",
    "stored_data",
    "blocking_method_ok",
    "twice_signal",
)
