import simplejson as json
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.template import RequestContext

# ZeroMQ Connection
from gevent import spawn
from gevent_zeromq import zmq

context = zmq.Context()
publisher = context.socket(zmq.PUB)
publisher.bind("ipc://127.0.0.1:5000")

# Message Coroutines

def broadcastCommand(socketio, command):
    publisher.send(str(command))

def commandListner(socketio):
    context = zmq.Context()
    subscriber = context.socket(zmq.SUB)
    subscriber.connect("ipc://127.0.0.1:5000")

    # setsockopt doesn't like unicode
    subscriber.setsockopt(zmq.SUBSCRIBE, "")

    while True:
        msg = subscriber.recv()
        if msg:
            socketio.send(msg)

def index(request, template_name='template.html'):
    context = { }

    return render_to_response(template_name, context,
            context_instance=RequestContext(request))

# SocketIO Handler

def socketio(request):
    socketio = request.environ['socketio']

    while True:
        raw_message = socketio.recv()

        if len(raw_message) == 1:

            try:
                message = json.loads(str(raw_message[0]))[0]
                command, args = message
            except json.JSONDecodeError:
                print "Not well formed", message

            if command == 'join_session':
                socketio.send(json.dumps([['sync_end',[]]]))
                spawn(commandListner, socketio)
            elif command in ("insert", "delete", "undo"):
                spawn(broadcastCommand, socketio, raw_message[0])

        else:
            if not socketio.connected():
                socketio.broadcast({'announcement': socketio.session.session_id + ' disconnected'})

    return HttpResponse()
