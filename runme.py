#!/usr/bin/env python
# encoding: utf-8
"""
This small app is used to start the GUI and the Backend in different process.
"""
import multiprocessing

from app import run_app
from backend import run_backend


if __name__ == '__main__':
    gui_process = multiprocessing.Process(target=run_app)
    gui_process.start()

    backend_process = multiprocessing.Process(target=run_backend)
    backend_process.start()
