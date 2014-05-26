#!/usr/bin/env python
# encoding: utf-8

import zmq

from signaler import Signaler

from utils import get_log_handler
logger = get_log_handler(__name__)


class Backend(object):
    """
    Backend server.
    Receives signals from backend_proxy and emit signals if needed.
    """
    PORT = '5556'

    API = (
        'test_api_call',
        'demo_api_call',
    )

    def __init__(self):
        self._signaler = Signaler()

        # ZMQ stuff
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://*:%s" % self.PORT)

        while True:
            #  Wait for next request from client
            message = socket.recv()
            logger.debug("Received request: '{0}'".format(message))
            # socket.send("World from %s" % self.PORT)
            socket.send("OK")
            self._process_message(message)

    def _process_message(self, msg):
        if msg not in self.API:
            self._signaler.signal(Signaler.invalid_api_call)

        if msg == 'test_api_call':
            self.test_api_call()

    def test_api_call(self):
        self._signaler.signal(Signaler.api_call_ok)


if __name__ == '__main__':
    backend = Backend()
