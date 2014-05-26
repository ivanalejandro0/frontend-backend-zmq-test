import zmq

from utils import get_log_handler
logger = get_log_handler(__name__)


class Signaler(object):
    """
    Signaler client.
    Receives signals from the backend and sends to the signaling server.
    """
    PORT = "5667"
    SERVER = "tcp://localhost:%s" % PORT

    api_call_ok = 'API_CALL_OK'
    invalid_api_call = 'INVALID_API_CALL'

    def __init__(self):
        """
        Initialize the ZMQ socket to talk to the signaling server.
        """
        context = zmq.Context()
        logger.debug("Connecting to signaling server...")
        socket = context.socket(zmq.REQ)
        socket.connect(self.SERVER)
        self._socket = socket

    def signal(self, signal):
        """
        Sends a signal to the signaling server.

        :param signal: the signal to send.
        :type signal: str
        """
        logger.debug("Signaling '{0}'".format(signal))
        self._socket.send(signal)

        #  Get the reply.
        response = self._socket.recv()
        msg = "Received reply for '{0}' -> '{1}'".format(signal, response)
        logger.debug(msg)
