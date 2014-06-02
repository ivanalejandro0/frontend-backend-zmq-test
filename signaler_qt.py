#!/usr/bin/env python
# encoding: utf-8
import zmq

from PySide import QtCore

from api import SIGNALS
from utils import get_log_handler
logger = get_log_handler(__name__)


class SignalerQt(QtCore.QThread):
    """
    Signaling server.
    Receives signals from the signaling client and emit Qt signals for the GUI.
    """
    PORT = "5667"
    BIND_ADDR = "tcp://*:%s" % PORT

    ###########################################################################
    # List of possible Qt signals to emit:
    test_signal_1 = QtCore.Signal()
    test_signal_2 = QtCore.Signal()
    test_signal_3 = QtCore.Signal(object)
    sig_blocking_method = QtCore.Signal()
    # end list of possible Qt signals to emit.
    ###########################################################################

    def __init__(self):
        QtCore.QThread.__init__(self)
        self._stop = False

    def run(self):
        """
        Start a loop to process the ZMQ requests from the signaler client.
        """
        logger.debug("Running SignalerQt loop")
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind(self.BIND_ADDR)

        while not self._stop:
            # Wait for next request from client
            request = socket.recv()
            logger.debug("Received request: '{0}'".format(request))
            socket.send("OK")
            self._process_request(request)

    def stop(self):
        """
        Stop the SignalerQt blocking loop.
        """
        self._stop = True

    def _process_request(self, request_json):
        """
        Process a request and call the according method with the given
        parameters.

        :param request_json: a json specification of a request.
        :type request_json: str
        """
        try:
            request = zmq.utils.jsonapi.loads(request_json)
            signal = request['signal']
            data = request['data']
        except Exception:
            msg = "Malformed JSON data in Signaler request '{0}'"
            msg = msg.format(request_json)
            logger.critical(msg)
            raise

        if signal not in SIGNALS:
            logger.error("Unknown signal received, '{0}'".format(signal))
            return

        try:
            qt_signal = getattr(self, signal)
        except Exception:
            logger.warning("Signal not implemented, '{0}'".format(signal))
            return

        logger.debug("Emitting '{0}'".format(signal))
        if not data:
            qt_signal.emit()
        else:
            qt_signal.emit(data)
