frontend-backend-zmq-test
=========================

A basic app separation in frontend/backend that communicates the moving parts using zmq and qt signals.

Files explanation
-----------------

### Frontend:

<dl>
  <dt>app.py</dt>
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
</dl>

### Utilities:

<dl>
  <dt>utils.py</dt>
  <dd>Logging utility.</dd>

  <dt>requirements.txt</dt>
  <dd>Requirements file to install dependencies using pip.</dd>

  <dt>pyside-to-virtualenv.sh</dt>
  <dd>Symlinks PySide from global installation into virtualenv site-packages.</dd>
</dl>


Diagram
-------

![Diagram](https://raw.githubusercontent.com/ivanalejandro0/frontend-backend-zmq-test/master/frontend-backend-zmq-test.png)

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
