frontend-backend-zmq-test
=========================

A basic app separation in frontend/backend that communicates the moving parts using zmq and qt signals.

Frontend
--------
* app.py
* backend_proxy.py
* signaler_qt.py

Backend
-------
* backend.py
* signaler.py

Instructions
------------
Run in different consoles:

    python app.py
    python backend.py


Requirements
------------
* pyzmq
* pyside
* twisted
