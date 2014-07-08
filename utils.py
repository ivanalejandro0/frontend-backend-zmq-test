#!/usr/bin/env python
# encoding: utf-8

import logging
import os
import shutil

import zmq.auth

# keys_dir = os.path.join(base_dir, 'zmq_certificates')
KEYS_DIR = 'zmq_certificates'


def generate_certificates():
    """
    Generate client and server CURVE certificate files.
    """
    # Create directory for certificates, remove old content if necessary
    if os.path.exists(KEYS_DIR):
        shutil.rmtree(KEYS_DIR)
    os.mkdir(KEYS_DIR)

    # create new keys in certificates dir
    # public_file, secret_file = create_certificates(...)
    zmq.auth.create_certificates(KEYS_DIR, "frontend")
    zmq.auth.create_certificates(KEYS_DIR, "backend")


def get_frontend_certificates():
    """
    Return the frontend's public and secret certificates.
    """
    frontend_secret_file = os.path.join(KEYS_DIR, "frontend.key_secret")
    public, secret = zmq.auth.load_certificate(frontend_secret_file)
    return public, secret


def get_backend_certificates(base_dir='.'):
    """
    Return the backend's public and secret certificates.
    """
    backend_secret_file = os.path.join(KEYS_DIR, "backend.key_secret")
    public, secret = zmq.auth.load_certificate(backend_secret_file)
    return public, secret


def get_log_handler(name):
    level = logging.DEBUG
    # level = logging.WARNING

    # Create logger and formatter
    logger = logging.getLogger(name)
    logger.setLevel(level)
    # levelname length == 8, since 'CRITICAL' is the longest
    log_format = ('%(asctime)s - %(levelname)-8s - '
                  'L#%(lineno)-4s : %(name)s:%(funcName)s() - %(message)s')
    formatter = logging.Formatter(log_format)

    # Console handler
    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(formatter)
    logger.addHandler(console)
    logger.debug('Console handler plugged!')

    return logger
