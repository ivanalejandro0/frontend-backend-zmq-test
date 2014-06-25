#!/usr/bin/env python
# encoding: utf-8
import Queue
import threading
import time

import zmq

from api import SIGNALS
from utils import get_log_handler, get_frontend_certificates
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

        # public, secret = zmq.curve_keypair()
        client_keys = zmq.curve_keypair()
        socket.curve_publickey = client_keys[0]
        socket.curve_secretkey = client_keys[1]

        # The client must know the server's public key to make a CURVE
        # connection.
        public, _ = get_frontend_certificates()
        socket.curve_serverkey = public

        socket.setsockopt(zmq.RCVTIMEO, 1000)
        socket.connect(self.SERVER)
        self._socket = socket

        self._signal_queue = Queue.Queue()

        self._do_work = False  # used to stop the worker loop.
        self._worker_signaler = threading.Thread(target=self._worker)

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

        # queue the call in order to handle the request in a thread safe way.
        self._signal_queue.put(request_json)

    def _worker(self):
        """
        Worker loop that processes the Queue of pending requests to do.
        """
        while self._do_work:
            try:
                request = self._signal_queue.get(block=False)
                self._send_request(request)
            except Queue.Empty:
                pass
            time.sleep(0.01)

        logger.debug("Signaler thread stopped.")

    def start(self):
        """
        Start the Signaler worker.
        """
        self._do_work = True
        self._worker_signaler.start()

    def stop(self):
        """
        Stop the Signaler worker.
        """
        self._do_work = False

    def _send_request(self, request):
        """
        Send the given request to the server.
        This is used from a thread safe loop in order to avoid sending a
        request without receiving a response from a previous one.

        :param request: the request to send.
        :type request: str
        """
        logger.debug("Signaling '{0}'".format(request))
        self._socket.send(request)

        # Get the reply.
        try:
            response = self._socket.recv()
            msg = "Received reply for '{0}' -> '{1}'".format(request, response)
            logger.debug(msg)
        except zmq.error.Again as e:
            msg = "Timeout error contacting signaler. {0!r}".format(e)
            logger.critical(msg)
