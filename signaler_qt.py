#!/usr/bin/env python
# encoding: utf-8
from PySide import QtCore

import zmq
from zmq.auth.thread import ThreadAuthenticator

from api import SIGNALS
from utils import get_log_handler, get_frontend_certificates
logger = get_log_handler(__name__)


class SignalerQt(QtCore.QThread):
    """
    Signaling server.
    Receives signals from the signaling client and emit Qt signals for the GUI.
    """
    PORT = "5667"
    BIND_ADDR = "tcp://*:%s" % PORT

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

        # Start an authenticator for this context.
        auth = ThreadAuthenticator(context)
        auth.start()
        auth.allow('127.0.0.1')

        # Tell authenticator to use the certificate in a directory
        auth.configure_curve(domain='*', location=zmq.auth.CURVE_ALLOW_ANY)
        public, secret = get_frontend_certificates()
        socket.curve_publickey = public
        socket.curve_secretkey = secret
        socket.curve_server = True  # must come before bind

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
        if data is None:
            qt_signal.emit()
        else:
            qt_signal.emit(data)


class DemoSignalerQt(SignalerQt):
    """
    Signaling server subclass, used to defines the API signals.
    """
    ###########################################################################
    # List of possible Qt signals to emit:
    add_result = QtCore.Signal(object)
    reset_ok = QtCore.Signal()
    stored_data = QtCore.Signal(object)
    blocking_method_ok = QtCore.Signal()
    twice_signal = QtCore.Signal()
    # end list of possible Qt signals to emit.
    ###########################################################################
