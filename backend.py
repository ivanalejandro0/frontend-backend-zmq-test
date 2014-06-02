#!/usr/bin/env python
# encoding: utf-8
import zmq

from signaler import Signaler

from api import API
from utils import get_log_handler
logger = get_log_handler(__name__)


class Backend(object):
    """
    Backend server.
    Receives signals from backend_proxy and emit signals if needed.
    """
    PORT = '5556'
    BIND_ADDR = "tcp://*:%s" % PORT

    def __init__(self):
        """
        Backend constructor, create needed instances.
        """
        self._signaler = Signaler()
        self._running = False

    def run(self):
        """
        Start the ZMQ server and run the blocking loop to handle requests.
        """
        logger.debug("Starting ZMQ loop...")
        # ZMQ stuff
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind(self.BIND_ADDR)

        self._running = True
        while self._running:
            #  Wait for next request from client
            request = socket.recv()
            logger.debug("Received request: '{0}'".format(request))
            socket.send("OK")
            self._process_request(request)

    def stop(self):
        """
        Stop the server and request parsing loop.
        """
        self._running = False

    def _process_request(self, request_json):
        """
        Process a request and call the according method with the given
        parameters.

        :param request_json: a json specification of a request.
        :type request_json: str
        """
        try:
            request = zmq.utils.jsonapi.loads(request_json)
            api_method = request['api_method']
            args = request['arguments']
        except Exception:
            msg = "Malformed JSON data in Backend request '{0}'"
            msg = msg.format(request_json)
            logger.critical(msg)
            raise

        if api_method not in API:
            self._signaler.signal(Signaler.invalid_api_call)
            logger.error("Invalid API call '{0}'".format(api_method))
            return

        logger.debug("Calling '{0}'".format(api_method))
        method = getattr(self, api_method)
        if args:
            # TODO: this should queue the call in a thread or something, that
            # way we don't block until the control is returned to this place.
            method(args)
        else:
            method()

    ###########################################################################
    # List of possible methods to use, we MUST implement ALL the API methods.
    # Otherwise, the call will be considered as valid in the backend_proxy and
    # will fail in here, while trying to run it.

    def test_method_1(self):
        self._signaler.signal(self._signaler.test_signal_1)

    def test_method_2(self):
        self._signaler.signal(self._signaler.test_signal_2)
        self._signaler.signal(self._signaler.test_signal_4)

    def ask_some_data(self):
        self._signaler.signal(self._signaler.test_signal_3, 'Lorem Data')


def run_backend():
    backend = Backend()
    backend.run()


if __name__ == '__main__':
    run_backend()
