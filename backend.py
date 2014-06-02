#!/usr/bin/env python
# encoding: utf-8
import Queue

from twisted.internet import reactor, threads
from twisted.internet.task import LoopingCall

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

        self._ongoing_defers = []
        self._call_queue = Queue.Queue()
        self._worker = LoopingCall(self._process_queue)

    def _start_zmq_loop(self):
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

    def run(self):
        """
        Start the ZMQ server and run the blocking loop to handle requests.
        """
        threads.deferToThread(self._start_zmq_loop)

        logger.debug("Starting queue processor...")
        self._worker.start(0.01)

        reactor.run()

    def stop(self):
        """
        Stop the server and request parsing loop.
        """
        self._running = False

        if self._worker.running:
            self._worker.stop()

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
            kwargs = request['arguments']
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
        if kwargs:
            method(kwargs)
        else:
            method()

    def _process_queue(self):
        """
        Process the call queue and run waiting operations in a thread to avoid
        blocking.

        Each item of the queue is a tuple with:
            [0] callable name
            [1] dict with arguments to forward to the callable
        """
        try:
            item = self._call_queue.get(block=False)
            logger.debug("Queue item: {0}".format(item))
            func = getattr(self, item[0])

            method = func
            if len(item) > 1:
                kwargs = item[1]
                method = lambda: func(**kwargs)

            # run the action in a thread and keep track of it
            d = threads.deferToThread(method)
            d.addCallback(self._done_action, d)
            d.addErrback(self._done_action, d)
            self._ongoing_defers.append(d)
        except Queue.Empty:
            # If it's just empty we don't have anything to do.
            pass
        except Exception as e:
            logger.exception("Unexpected exception: {0!r}".format(e))

    def _done_action(self, failure, d):
        """
        Remove the defer from the ongoing list.

        :param failure: the failure that triggered the errback.
                        None if no error.
        :type failure: twisted.python.failure.Failure
        :param d: defer to remove
        :type d: twisted.internet.defer.Deferred
        """
        if failure is not None:
            logger.error("There was a failure - {0!r}".format(failure))
            logger.error(failure.getTraceback())

        if d in self._ongoing_defers:
            self._ongoing_defers.remove(d)

    ###########################################################################
    # List of possible methods to use, we MUST implement ALL the API methods.
    # Otherwise, the call will be considered as valid in the backend_proxy and
    # will fail in here, while trying to run it.

    def _reset(self):
        """
        Signal a reset_ok signal.
        """
        self._signaler.signal(self._signaler.reset_ok)

    def reset(self):
        """
        Test the signaling system with a simple request/reply.
        """
        self._call_queue.put(('_reset', ))

    def _add(self, a, b):
        """
        This adds two parameters and signals the result.

        :param a: first operand
        :type a: int
        :param b: second operand
        :type b: int
        """
        self._signaler.signal(self._signaler.add_result, a+b)

    def add(self, data):
        """
        This adds two parameters and signals the result.

        :param data: dict of parameters needed by _add.
        :type data: dict.
        """
        self._call_queue.put(('_add', data))

    def _get_stored_data(self):
        """
        Signal back some test data.
        """
        self._signaler.signal(self._signaler.stored_data, 'Lorem Data')

    def get_stored_data(self):
        """
        Signal back some test data.
        """
        self._call_queue.put(('_get_stored_data', ))

    def _blocking_method(self, data, delay):
        """
        This method blocks for `delay` seconds.

        :param data: some data
        :type data: str
        :param delay: this indicates how much time we need to wait until return
        :type delay: int
        """
        logger.debug("blocking method start")
        logger.debug("data: {0} - delay:{1}".format(data, delay))
        import time
        time.sleep(delay)
        logger.debug("blocking method end")
        self._signaler.signal(self._signaler.blocking_method_ok)

    def blocking_method(self, data):
        """
        :param data: dict of parameters needed by _blocking_method.
        :type data: dict.
        """
        self._call_queue.put(('_blocking_method', data))


def run_backend():
    backend = Backend()
    backend.run()


if __name__ == '__main__':
    run_backend()
