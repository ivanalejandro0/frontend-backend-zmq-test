#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import signal

from PySide import QtGui

# do this import after *any* other custom import so the logger gets set.
from utils import get_log_handler
logger = get_log_handler(__name__)

from backend import run_backend
from backend_proxy import BackendProxy
from signaler_qt import SignalerQt


class DemoWidget(QtGui.QWidget):
    """
    Demo class that creates a GUI with some buttons to do some test
    communication with the backend.
    """
    def __init__(self):
        QtGui.QWidget.__init__(self)

        self._backend_proxy = BackendProxy()

        self.init_gui()
        self._setup_signaler()

    def _setup_signaler(self):
        """
        Setup the SignalerQt instance to use, connect to signals and run
        blocking loop in a thread.
        """
        self._signaler_qt = SignalerQt()

        # Connect signals
        self._signaler_qt.test_signal_1.connect(self._on_test_signal_1)
        self._signaler_qt.test_signal_2.connect(self._on_test_signal_2)
        self._signaler_qt.test_signal_3.connect(self._on_test_signal_3)
        self._signaler_qt.sig_blocking_method.connect(
            self._on_sig_blocking_method)

        # we run the signaler server in a thread since has a blocking loop
        self._signaler_qt.start()

    def init_gui(self):
        """
        Initializes a minimal working GUI to interact with.
        """
        # create buttons
        pb_test1 = QtGui.QPushButton('Test 1')
        pb_test2 = QtGui.QPushButton('Test 2')
        pb_test3 = QtGui.QPushButton('Ask some data')
        pb_test4 = QtGui.QPushButton('Blocking method')

        # connect buttons with demo actions
        pb_test1.clicked.connect(self.test1)
        pb_test2.clicked.connect(self.test2)
        pb_test3.clicked.connect(self.test3)
        pb_test4.clicked.connect(self.test4)

        # define layout
        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(pb_test1)
        hbox.addWidget(pb_test2)
        hbox.addWidget(pb_test3)
        hbox.addWidget(pb_test4)

        vbox = QtGui.QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        # resize window
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Test window')

    def test1(self):
        logger.debug("calling: test_method_1")
        self._backend_proxy.test_method_1()

    def test2(self):
        logger.debug("calling: test_method_2")
        self._backend_proxy.test_method_2()

    def test3(self):
        logger.debug("calling: ask_some_data")
        self._backend_proxy.ask_some_data()

    def test4(self):
        logger.debug("calling: blocking_method")
        self._backend_proxy.blocking_method(data='blah', delay=5)

    def _on_test_signal_1(self):
        QtGui.QMessageBox.information(
            self, "Information", 'TEST_SIGNAL_1 received.')

    def _on_test_signal_2(self):
        QtGui.QMessageBox.information(
            self, "Information", 'TEST_SIGNAL_2 received.')

    def _on_test_signal_3(self, data):
        QtGui.QMessageBox.information(
            self, "Information",
            'TEST_SIGNAL_3 received.\nData: {0}'.format(data))

    def _on_sig_blocking_method(self):
        QtGui.QMessageBox.information(
            self, "Information", 'sig_blocking_method received.')


def run_app(should_run_backend=False):
    """
    Run the app and start the backend if specified.

    :param should_run_backend: whether we should run the backend or not.
    :type should_run_backend: bool
    """
    app = QtGui.QApplication(sys.argv)
    demo = DemoWidget()
    demo.show()

    # Ensure that the application quits using CTRL-C
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    if should_run_backend:
        import multiprocessing
        backend_process = multiprocessing.Process(target=run_backend)
        backend_process.start()

    sys.exit(app.exec_())


if __name__ == '__main__':
    """
    By default the app is started along the Backend.
    If you want to start the GUI and the Backend separately you can start the
    app with the `--no-backend` parameter and run the backend in other
    terminal. E.g.:
        python app.py --no-backend
        python backend.py
    """
    should_run_backend = True
    if len(sys.argv) > 1 and sys.argv[1] == '--no-backend':
        should_run_backend = False
    run_app(should_run_backend=should_run_backend)
