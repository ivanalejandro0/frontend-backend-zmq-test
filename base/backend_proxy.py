#!/usr/bin/env python
# encoding: utf-8
import functools
import Queue
import threading
import time

import zmq

from api import API, STOP_REQUEST
from certificates import get_backend_certificates
from utils import get_log_handler

logger = get_log_handler(__name__)


class BackendProxy(object):
    """
    The BackendProxy handles calls from the GUI and forwards (through ZMQ)
    to the backend.
    """
    PORT = '5556'
    SERVER = "tcp://localhost:%s" % PORT

    POLL_TIMEOUT = 1000  # ms
    POLL_TRIES = 3

    def __init__(self):
        self._socket = None

        # initialize ZMQ stuff:
        context = zmq.Context()
        logger.debug("Connecting to server...")
        socket = context.socket(zmq.REQ)

        # public, secret = zmq.curve_keypair()
        client_keys = zmq.curve_keypair()
        socket.curve_publickey = client_keys[0]
        socket.curve_secretkey = client_keys[1]

        # The client must know the server's public key to make a CURVE
        # connection.
        public, _ = get_backend_certificates()
        socket.curve_serverkey = public

        socket.setsockopt(zmq.RCVTIMEO, 1000)
        socket.connect(self.SERVER)
        self._socket = socket

        self._call_queue = Queue.Queue()
        self._worker_caller = threading.Thread(target=self._worker)
        self._worker_caller.start()

    def _worker(self):
        """
        Worker loop that processes the Queue of pending requests to do.
        """
        while True:
            try:
                request = self._call_queue.get(block=False)
                # break the loop after sending the 'stop' action to the
                # backend.
                if request == STOP_REQUEST:
                    break

                self._send_request(request)
            except Queue.Empty:
                pass
            time.sleep(0.01)

        logger.debug("BackendProxy worker stopped.")

    def _api_call(self, *args, **kwargs):
        """
        Call the `api_method` method in backend (through zmq).

        :param kwargs: named arguments to forward to the backend api method.
        :type kwargs: dict

        Note: is mandatory to have the kwarg 'api_method' defined.
        """
        if args:
            # Use a custom message to be more clear about using kwargs *only*
            raise Exception("All arguments need to be kwargs!")

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

        # queue the call in order to handle the request in a thread safe way.
        self._call_queue.put(request_json)

        if api_method == STOP_REQUEST:
            self._call_queue.put(STOP_REQUEST)

    def _send_request(self, request):
        """
        Send the given request to the server.
        This is used from a thread safe loop in order to avoid sending a
        request without receiving a response from a previous one.

        :param request: the request to send.
        :type request: str
        """
        logger.debug("Sending request to backend: {0}".format(request))
        self._socket.send(request)

        poll = zmq.Poller()
        poll.register(self._socket, zmq.POLLIN)

        reply = None
        tries = 0

        while True:
            socks = dict(poll.poll(self.POLL_TIMEOUT))
            if socks.get(self._socket) == zmq.POLLIN:
                reply = self._socket.recv()
                break

            tries += 1
            if tries < self.POLL_TRIES:
                logger.warning('Retrying receive... {0}/{1}'.format(
                    tries, self.POLL_TRIES))
            else:
                break

        if reply is None:
            msg = "Timeout error contacting backend."
            logger.critical(msg)
        else:
            msg = "Received reply for '{0}' -> '{1}'".format(request, reply)
            logger.debug(msg)

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
