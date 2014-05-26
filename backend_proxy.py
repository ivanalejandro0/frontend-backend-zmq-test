import zmq

from utils import get_log_handler
logger = get_log_handler(__name__)


class BackendProxy(object):
    """Docstring for BackendProxy. """
    PORT = '5556'

    API = (
        'test_api_call',
        'demo_api_call',
    )

    def __init__(self):
        self._socket = None

        # initialize ZMQ stuff:
        context = zmq.Context()
        logger.debug("Connecting to server...")
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:%s" % self.PORT)
        self._socket = socket

    def call(self, name):
        """
        Call the `name` method in backend (through zmq) or fail if the method
        name does not exist in the API.

        :param name: the name of the method to call.
        :type name: str
        """
        # if name not in self.API:
        #     raise Exception("Call to undefined API method.")
        # else:
        request = name
        msg = "Sending request '{0}'...".format(request)
        logger.debug(msg)
        self._socket.send(request)

        #  Get the reply.
        response = self._socket.recv()
        msg = "Received reply for '{0}' -> '{1}'".format(request, response)
        logger.debug(msg)

    def test_api_call(self):
        self.call('test_api_call')
