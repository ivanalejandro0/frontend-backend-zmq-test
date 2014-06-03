#!/usr/bin/env python
# encoding: utf-8
"""
This small app is used to start the GUI and the Backend in different process.
"""
import multiprocessing
import signal

import zmq

from app import run_app
from backend import run_backend


if __name__ == '__main__':
    # Ensure that the application quits using CTRL-C
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Create all the needed keypairs in here and send it to the process so they
    # can communicate each other securely.

    # public, secret = zmq.curve_keypair()
    backend_keys = zmq.curve_keypair()
    frontend_keys = zmq.curve_keypair()

    app = lambda: run_app(key_pair=frontend_keys,
                          backend_key=backend_keys[0])
    gui_process = multiprocessing.Process(target=app)
    gui_process.start()

    backend = lambda: run_backend(key_pair=backend_keys,
                                  frontend_key=frontend_keys[0])
    backend_process = multiprocessing.Process(target=backend)
    backend_process.start()
