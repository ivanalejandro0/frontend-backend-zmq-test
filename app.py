#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import signal

from twisted.internet import reactor, threads
from twisted.internet.task import LoopingCall

from PySide import QtCore, QtGui

# do this import after *any* other custom import so the logger gets set.
from utils import get_log_handler
logger = get_log_handler(__name__)

from backend_proxy import BackendProxy
from signaler_qt import SignalerQt


class DemoClass(QtGui.QWidget):
    """
    Demo class that creates a GUI with some buttons to do some test
    communication with the backend.
    """
    def __init__(self):
        QtGui.QWidget.__init__(self)

        # create needed objects and make connections
        self._backend_proxy = BackendProxy()
        self._signaler_qt = SignalerQt()
        self._signaler_qt.api_call_ok.connect(self._api_call_ok)
        self._signaler_qt.invalid_api_call.connect(self._api_call_error)

        self.init_gui()

        # run the signaler server in a thread since has a blocking loop
        threads.deferToThread(self._signaler_qt.run)

    def init_gui(self):
        # create buttons
        pb_test1 = QtGui.QPushButton('Test 1')
        pb_test2 = QtGui.QPushButton('Test 2')

        # connect buttons with demo actions
        pb_test1.clicked.connect(self.test)
        pb_test2.clicked.connect(self.demo)

        # define layout
        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(pb_test1)
        hbox.addWidget(pb_test2)

        vbox = QtGui.QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        # resize window
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Test window')

        self.show()

    def test(self):
        logger.debug("calling: test_api_call")
        self._backend_proxy.test_api_call()

    def demo(self):
        logger.debug("calling: demo_api_call")
        self._backend_proxy.call('demo_api_call-')

    def _api_call_ok(self):
        QtGui.QMessageBox.information(self, "Information", 'API call OK.')

    def _api_call_error(self):
        QtGui.QMessageBox.critical(self, "Error", 'Invalid API call.')


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    demo = DemoClass()

    # Ensure that the application quits using CTRL-C
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # import multiprocessing
    # backend = Backend()
    # multiprocessing.Process(target=backend.run)

    # using twisted's reactor to call the Qt's event processor since we are
    # not using the Qt reactor.
    l = LoopingCall(QtCore.QCoreApplication.processEvents, 0, 10)
    l.start(0.01)
    reactor.run()
