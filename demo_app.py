#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import signal
import time

from PySide import QtGui

# do this import after *any* other custom import so the logger gets set.
from utils import get_log_handler
logger = get_log_handler(__name__)

from backend import run_backend
from backend_proxy import BackendProxy
from signaler_qt import DemoSignalerQt


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
        self._signaler_qt = signaler = DemoSignalerQt()

        # Connect signals
        signaler.add_result.connect(self._on_add_result)
        signaler.reset_ok.connect(self._on_reset_ok)
        signaler.stored_data.connect(self._on_stored_data)
        signaler.blocking_method_ok.connect(self._on_blocking_method_ok)

        # we run the signaler server in a thread since has a blocking loop
        self._signaler_qt.start()

    def init_gui(self):
        """
        Initializes a minimal working GUI to interact with.
        """
        # create buttons
        pb_test1 = QtGui.QPushButton('Reset calculator')
        pb_test2 = QtGui.QPushButton('Add 2+2')
        pb_test3 = QtGui.QPushButton('Giveme stored data')
        pb_test4 = QtGui.QPushButton('Blocking method')
        pb_test5 = QtGui.QPushButton('Signal twice, threaded')

        # connect buttons with demo actions
        pb_test1.clicked.connect(self._call_reset)
        pb_test2.clicked.connect(self._call_add)
        pb_test3.clicked.connect(self._call_get_data)
        pb_test4.clicked.connect(self._call_block_call)

        pb_test5.clicked.connect(self._call_twice_01)
        pb_test5.clicked.connect(self._call_twice_02)

        # define layout
        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(pb_test1)
        hbox.addWidget(pb_test2)
        hbox.addWidget(pb_test3)
        hbox.addWidget(pb_test4)
        hbox.addWidget(pb_test5)

        vbox = QtGui.QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        # resize window
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Test window')

    def closeEvent(self, e):
        """
        Reimplementation of closeEvent.
        """
        logger.debug("Closing app")
        self._signaler_qt.stop()
        self._backend_proxy.stop()
        time.sleep(0.05)  # give the thread a little time to finish.

        QtGui.QWidget.closeEvent(self, e)

    ####################
    # Backend calls, on buttons clicked

    def _call_reset(self):
        logger.debug("calling: reset")
        self._backend_proxy.reset()

    def _call_add(self):
        logger.debug("calling: add(2, 2)")
        self._backend_proxy.add(a=2, b=2)

    def _call_get_data(self):
        logger.debug("calling: get_stored_data")
        self._backend_proxy.get_stored_data()

    def _call_block_call(self):
        logger.debug("calling: blocking_method")
        self._backend_proxy.blocking_method(data=u'bláḩ', delay=19)

    def _call_twice_01(self):
        logger.debug("calling: twice_01")
        self._backend_proxy.twice_01()

    def _call_twice_02(self):
        logger.debug("calling: twice_02")
        self._backend_proxy.twice_02()

    ####################
    # Backend signals handlers

    def _on_add_result(self, data):
        QtGui.QMessageBox.information(
            self, "Information",
            'add_result received.\nData: {0}'.format(data))

    def _on_reset_ok(self):
        QtGui.QMessageBox.information(
            self, "Information", 'reset_ok received.')

    def _on_stored_data(self, data):
        QtGui.QMessageBox.information(
            self, "Information",
            'stored_data received.\nData: {0}'.format(data))

    def _on_blocking_method_ok(self):
        QtGui.QMessageBox.information(
            self, "Information", 'blocking_method_ok received.')


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
