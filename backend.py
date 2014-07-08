#!/usr/bin/env python
# encoding: utf-8
import json
import signal
import time

from twisted.internet import defer, reactor, threads

import zmq
from zmq.auth.thread import ThreadAuthenticator

from signaler import Signaler

from api import API
from utils import get_log_handler, get_backend_certificates
logger = get_log_handler(__name__)


class Backend(object):
    """
    Backend server.
    Receives signals from backend_proxy and emit signals if needed.
    """
    PORT = '5556'
    BIND_ADDR = "tcp://127.0.0.1:%s" % PORT

    def __init__(self):
        """
        Backend constructor, create needed instances.
        """
        self._signaler = Signaler()

        self._do_work = False  # used to stop the worker thread.
        self._zmq_socket = None

        self._ongoing_defers = []
        self._init_zmq()

    def _init_zmq(self):
        """
        Configure the zmq components and connection.
        """
        context = zmq.Context()
        socket = context.socket(zmq.REP)

        # Start an authenticator for this context.
        auth = ThreadAuthenticator(context)
        auth.start()
        auth.allow('127.0.0.1')

        # Tell authenticator to use the certificate in a directory
        auth.configure_curve(domain='*', location=zmq.auth.CURVE_ALLOW_ANY)
        public, secret = get_backend_certificates()
        socket.curve_publickey = public
        socket.curve_secretkey = secret
        socket.curve_server = True  # must come before bind

        socket.bind(self.BIND_ADDR)

        self._zmq_socket = socket

    def _worker(self):
        """
        Receive requests and send it to process.
        """
        while self._do_work:
            # Wait for next request from client
            try:
                request = self._zmq_socket.recv(zmq.NOBLOCK)
                self._zmq_socket.send("OK")
                logger.debug("Received request: '{0}'".format(request))
                self._process_request(request)
            except zmq.ZMQError as e:
                if e.errno != zmq.EAGAIN:
                    raise
            time.sleep(0.01)

    def _stop_reactor(self):
        """
        Stop the Twisted reactor, but first wait a little for some threads to
        complete their work.

        Note: this method needs to be run in a different thread so the
        time.sleep() does not block and other threads can finish.
        i.e.:
            use threads.deferToThread(this_method) instead of this_method()
        """
        wait_max = 5  # seconds
        wait_step = 0.5
        wait = 0
        while self._ongoing_defers and wait < wait_max:
            time.sleep(wait_step)
            wait += wait_step
            msg = "Waiting for running threads to finish... {0}/{1}"
            msg = msg.format(wait, wait_max)
            logger.debug(msg)

        # after a timeout we shut down the existing threads.
        for d in self._ongoing_defers:
            d.cancel()

        reactor.stop()
        logger.debug("Twisted reactor stopped.")

    def run(self):
        """
        Start the ZMQ server and run the loop to handle requests.
        """
        self._signaler.start()
        self._do_work = True
        threads.deferToThread(self._worker)
        reactor.run()

    def stop(self):
        """
        Stop the server and the zmq request parse loop.
        """
        logger.debug("STOP received.")
        self._signaler.stop()
        self._do_work = False
        threads.deferToThread(self._stop_reactor)

    def _process_request(self, request_json):
        """
        Process a request and call the according method with the given
        parameters.

        :param request_json: a json specification of a request.
        :type request_json: str
        """
        try:
            # request = zmq.utils.jsonapi.loads(request_json)
            # We use stdlib's json to ensure that we get unicode strings
            request = json.loads(request_json)
            api_method = request['api_method']
            kwargs = request['arguments'] or None
        except Exception:
            msg = "Malformed JSON data in Backend request '{0}'"
            msg = msg.format(request_json)
            logger.critical(msg)
            raise

        if api_method not in API:
            logger.error("Invalid API call '{0}'".format(api_method))
            return

        self._run_in_thread((api_method, kwargs))

    def _run_in_thread(self, cmd):
        """
        Run the method name in a thread with the given arguments.

        :param cmd: a tuple containing (method, arguments)
        :type cmd: tuple (str, dict or None)
        """
        func = getattr(self, cmd[0])
        kwargs = cmd[1]

        method = func
        if kwargs is not None:
            method = lambda: func(**kwargs)

        logger.debug("Running method: '{0}' "
                     "with args: '{1}' in a thread".format(cmd[0], kwargs))
        # run the action in a thread and keep track of it
        d = threads.deferToThread(method)
        d.addCallback(self._done_action, d)
        d.addErrback(self._done_action, d)
        self._ongoing_defers.append(d)

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
            if failure.check(defer.CancelledError):
                logger.debug("A defer was cancelled.")
            else:
                logger.error("There was a failure - {0!r}".format(failure))
                logger.error(failure.getTraceback())

        if d in self._ongoing_defers:
            self._ongoing_defers.remove(d)


class DemoBackend(Backend):
    """
    Backend server subclass, used to implement the API methods.
    """
    ###########################################################################
    # List of possible methods to use, we MUST implement ALL the API methods.
    # Otherwise, the call will be considered as valid in the backend_proxy and
    # will fail in here, while trying to run it.

    def reset(self):
        """
        Signal a reset_ok signal.
        Helper to test the signaling system with a simple request/reply.
        """
        self._signaler.signal(self._signaler.reset_ok)

    def add(self, a, b):
        """
        This adds two parameters and signals the result.

        :param a: first operand
        :type a: int
        :param b: second operand
        :type b: int
        """
        self._signaler.signal(self._signaler.add_result, a+b)

    def get_stored_data(self):
        """
        Signal back some test data.
        """
        self._signaler.signal(self._signaler.stored_data, 'Lorem Data')

    def blocking_method(self, data, delay):
        """
        This method blocks for `delay` seconds.

        :param data: some data
        :type data: unicode
        :param delay: this indicates how much time we need to wait until return
        :type delay: int
        """
        assert isinstance(data, unicode)  # ensure parameter type
        logger.debug("blocking method start")
        logger.debug("data: {0!r} - delay:{1}".format(data, delay))
        import time
        time.sleep(delay)  # simulate some work
        logger.debug("blocking method end")
        self._signaler.signal(self._signaler.blocking_method_ok)

    def twice_01(self):
        self._signaler.signal(self._signaler.twice_signal)

    def twice_02(self):
        self._signaler.signal(self._signaler.twice_signal)


def run_backend():
    # Ensure that the application quits using CTRL-C
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    backend = DemoBackend()
    backend.run()


if __name__ == '__main__':
    run_backend()
