#!/usr/bin/env python
# encoding: utf-8
from PySide import QtCore

from signaler_qt import SignalerQt


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
