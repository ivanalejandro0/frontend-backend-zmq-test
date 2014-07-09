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

If you run use a virtualenv you may want to use the global installation of
PySide. The pyside-to-virtualenv.sh helper script links the global libraries
into the virtualenv.


Files explanation
-----------------

<dl>
  <dt>base/backend.py</dt>
  <dd>Receives signals from backend_proxy and emit signals if needed.</dd>

  <dt>base/backend_proxy.py</dt>
  <dd>Handle calls from the GUI and forwards (through ZMQ) to the backend.</dd>

  <dt>base/signaler.py</dt>
  <dd>Receives signals from the backend and sends to the signaling server.</dd>

  <dt>base/signaler_qt.py</dt>
  <dd>Receives signals from the signaling client and emit Qt signals for the GUI.</dd>

  <dt>base/certificates.py</dt>
  <dd>Utilities for ZMQ auth.</dd>

  <dt>demo_app.py</dt>
  <dd>Demo class that creates a GUI with some buttons to do some test communication with the backend.</dd>

  <dt>demo_backend.py</dt>
  <dd>Demo implementation of Backend.</dd>

  <dt>demo_signaler_qt.py</dt>
  <dd>Demo implementation of the SignalerQt</dd>

  <dt>api.py</dt>
  <dd>Definition of available API and SIGNALS in the backend.</dd>

  <dt>runme.py</dt>
  <dd>Helper app to run the GUI and the Backend in different process.</dd>

  <dt>utils.py</dt>
  <dd>Utilities for logging.</dd>

  <dt>requirements.txt</dt>
  <dd>Requirements file to install dependencies using pip.</dd>

  <dt>pyside-to-virtualenv.sh</dt>
  <dd>Symlinks PySide from global installation into virtualenv site-packages.</dd>
</dl>


Diagrams
--------

### Components

![Components](https://raw.githubusercontent.com/ivanalejandro0/frontend-backend-zmq-test/master/imgs/components.png)

### Communication flow

![Communication flow](https://raw.githubusercontent.com/ivanalejandro0/frontend-backend-zmq-test/master/imgs/communication-flow.png)
