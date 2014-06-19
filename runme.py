#!/usr/bin/env python
# encoding: utf-8
"""
This small app is used to start the GUI and the Backend in different process.
"""
import multiprocessing
import signal

from demo_app import run_app
from backend import run_backend
from utils import generate_certificates


if __name__ == '__main__':
    # Ensure that the application quits using CTRL-C
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    generate_certificates()

    gui_process = multiprocessing.Process(target=run_app)
    gui_process.start()

    backend_process = multiprocessing.Process(target=run_backend)
    backend_process.start()
