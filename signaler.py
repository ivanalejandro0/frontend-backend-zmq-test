#!/usr/bin/env python
# encoding: utf-8
import zmq

from api import SIGNALS
from utils import get_log_handler
logger = get_log_handler(__name__)


class Signaler(object):
    """
    Signaler client.
    Receives signals from the backend and sends to the signaling server.
    """
    PORT = "5667"
    SERVER = "tcp://localhost:%s" % PORT

    def __init__(self):
        """
        Initialize the ZMQ socket to talk to the signaling server.
        """
        context = zmq.Context()
        logger.debug("Connecting to signaling server...")
        socket = context.socket(zmq.REQ)
        socket.setsockopt(zmq.RCVTIMEO, 1000)
        socket.connect(self.SERVER)
        self._socket = socket

    def __getattribute__(self, name):
        """
        This allows the user to do:
            S = Signaler()
            S.SOME_SIGNAL

        Just by having defined 'some_signal' in _SIGNALS

        :param name: the attribute name that is requested.
        :type name: str
        """
        if name in SIGNALS:
            return name
        else:
            return object.__getattribute__(self, name)

    def signal(self, signal, data=None):
        """
        Sends a signal to the signaling server.

        :param signal: the signal to send.
        :type signal: str
        """
        if signal not in SIGNALS:
            raise Exception("Unknown signal: '{0}'".format(signal))

        request = {
            'signal': signal,
            'data': data,
        }

        try:
            request_json = zmq.utils.jsonapi.dumps(request)
        except Exception as e:
            msg = ("Error serializing request into JSON.\n"
                   "Exception: {0} Data: {1}")
            msg = msg.format(e, request)
            logger.critical(msg)
            raise

        logger.debug("Signaling '{0}'".format(request_json))
        self._socket.send(request_json)

        # Get the reply.
        # TODO: handle this in a non-blocking way.
        try:
            response = self._socket.recv()
            msg = "Received reply for '{0}' -> '{1}'".format(request, response)
            logger.debug(msg)
        except zmq.error.Again as e:
            msg = "Timeout error contacting signaler. {0!r}".format(e)
            logger.critical(msg)
