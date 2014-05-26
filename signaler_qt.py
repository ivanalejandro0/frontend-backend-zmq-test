import zmq

from PySide import QtCore

from utils import get_log_handler
logger = get_log_handler(__name__)


class SignalerQt(QtCore.QObject):
    """
    Signaling server.
    Receives signals from the signaling client and emit Qt signals for the GUI.
    """
    PORT = "5667"
    BIND_ADDR = "tcp://*:%s" % PORT

    # List of possible Qt signals to emit:
    api_call_ok = QtCore.Signal()
    invalid_api_call = QtCore.Signal()

    def __init__(self):
        QtCore.QObject.__init__(self)

    def run(self):
        """
        Start a loop to process the ZMQ requests from the signaler client.
        """
        logger.debug("Running SignalerQt loop")
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind(self.BIND_ADDR)

        while True:
            #  Wait for next request from client
            message = socket.recv()
            logger.debug("Received request: '{0}'".format(message))
            self._parse_signal(message)
            socket.send("OK")

    def _parse_signal(self, signal):
        """
        Parse the signal and emit a Qt signal if needed.

        :param signal: the signal to parse.
        :type signal: str
        """
        if signal == 'API_CALL_OK':
            self.api_call_ok.emit()
        if signal == 'INVALID_API_CALL':
            self.invalid_api_call.emit()
        else:
            logger.error("Unknown signal: '{0}'".format(signal))
