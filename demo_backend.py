#!/usr/bin/env python
# encoding: utf-8
import signal

from backend import Backend
from utils import get_log_handler
logger = get_log_handler(__name__)


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
