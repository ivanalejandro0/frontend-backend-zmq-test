frontend-backend-zmq-test
=========================

A (kind of) basic app that separates the GUI (frontend) and the logic/hard-work
(backend) in different process and communicates the moving parts using zmq and
qt signals.

The frontend and the backend are started in different processes using
`multiprocessing`.

The communication is handled using `pyzmq` and is secured using the ZMQ's CURVE
security mechanism.

Each task that the backend needs to work in is started in a `twisted` thread.

Files explanation
-----------------

### Frontend:

<dl>
  <dt>demo_app.py</dt>
  <dd>Demo class that creates a GUI with some buttons to do some test communication with the backend.</dd>

  <dt>backend_proxy.py</dt>
  <dd>Handle calls from the GUI and forwards (through ZMQ) to the backend.</dd>

  <dt>signaler_qt.py</dt>
  <dd>Receives signals from the signaling client and emit Qt signals for the GUI.</dd>
</dl>


### Backend:

<dl>
  <dt>backend.py</dt>
  <dd>Receives signals from backend_proxy and emit signals if needed.</dd>

  <dt>signaler.py</dt>
  <dd>Receives signals from the backend and sends to the signaling server.</dd>
</dl>



### Frontend and Backend:

<dl>
  <dt>api.py</dt>
  <dd>Definition of available API and SIGNALS in the backend.</dd>

  <dt>runme.py</dt>
  <dd>Helper app to run the GUI and the Backend in different process.</dd>
</dl>

### Utilities:

<dl>
  <dt>utils.py</dt>
  <dd>Utilities for logging and ZMQ auth.</dd>

  <dt>requirements.txt</dt>
  <dd>Requirements file to install dependencies using pip.</dd>

  <dt>pyside-to-virtualenv.sh</dt>
  <dd>Symlinks PySide from global installation into virtualenv site-packages.</dd>
</dl>


Diagrams
--------

### Components

![Components](https://raw.githubusercontent.com/ivanalejandro0/frontend-backend-zmq-test/master/components.png)

### Communication flow

![Communication flow](https://raw.githubusercontent.com/ivanalejandro0/frontend-backend-zmq-test/master/communication-flow.png)

Instructions
------------
You can run the `demo_app.py` file that uses a separate process for the backend:

    python demo_app.py


You can run in the GUI and the Backend in different consoles:

    python demo_app.py --no-backend
    python backend.py


Or you can use the `runme.py` helper that uses a process for the GUI and other process for the Backend:

    python runme.py


Requirements
------------
* pyzmq
* pyside
* twisted
