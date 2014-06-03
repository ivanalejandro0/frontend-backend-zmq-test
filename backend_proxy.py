#!/usr/bin/env python
# encoding: utf-8
import functools

import zmq

from api import API
from utils import get_log_handler
logger = get_log_handler(__name__)


class BackendProxy(object):
    """
    The BackendProxy handles calls from the GUI and forwards (through ZMQ)
    to the backend.
    """
    PORT = '5556'
    SERVER = "tcp://localhost:%s" % PORT

    def __init__(self):
        self._socket = None

        # initialize ZMQ stuff:
        context = zmq.Context()
        logger.debug("Connecting to server...")
        socket = context.socket(zmq.REQ)
        socket.setsockopt(zmq.RCVTIMEO, 1000)
        socket.connect(self.SERVER)
        self._socket = socket

    def _api_call(self, **kwargs):
        """
        Call the `api_method` method in backend (through zmq).

        :param kwargs: named arguments to forward to the backend api method.
        :type kwargs: dict
        """
        api_method = kwargs.pop('api_method', None)
        if api_method is None:
            raise Exception("Missing argument, no method name specified.")

        request = {
            'api_method': api_method,
            'arguments': kwargs,
        }

        try:
            request_json = zmq.utils.jsonapi.dumps(request)
        except Exception as e:
            msg = ("Error serializing request into JSON.\n"
                   "Exception: {0} Data: {1}")
            msg = msg.format(e, request)
            logger.critical(msg)
            raise

        logger.debug("Sending request to backend: {0}".format(request_json))
        self._socket.send(request_json)

        # Get the reply.
        # TODO: handle this in a non-blocking way.
        try:
            response = self._socket.recv()
            msg = "Received reply for '{0}' -> '{1}'".format(request, response)
            logger.debug(msg)
        except zmq.error.Again as e:
            msg = "Timeout error contacting backend. {0!r}".format(e)
            logger.critical(msg)

    def __getattribute__(self, name):
        """
        This allows the user to do:
            bp = BackendProxy()
            bp.some_method()

        Just by having defined 'some_method' in the API

        :param name: the attribute name that is requested.
        :type name: str
        """
        if name in API:
            return functools.partial(self._api_call, api_method=name)
        else:
            return object.__getattribute__(self, name)
