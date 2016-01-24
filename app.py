import time
from threading import Thread
from flask_socketio import SocketIO
from flask_bootstrap import Bootstrap
from flask import Flask, render_template
import RPi.GPIO as GPIO
import eventlet
eventlet.monkey_patch()


class WebApp:
    def __init__(self):
        print("Started webledbut")

        self.thread = None

        #to disable RuntimeWarning: This channel is already in use
        GPIO.setwarnings(False)

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(23, GPIO.OUT)
        GPIO.output(23, GPIO.LOW)
        GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        app = Flask(__name__)
        Bootstrap(app)
        app.config['DEBUG'] = False
        self.socketio = SocketIO(app, async_mode='eventlet')
        self.counter = 0

        print('Begin thread')
        if self.thread is None:
            print('create thread')
            thread = Thread(target=self.background_thread)
            thread.daemon = True
            thread.start()

        @app.before_first_request
        def initialize():
            print('Called only once, when the first request comes in')

        @app.route('/')
        def index():
            print("render index.html")
            return render_template("index.html", board="Raspberry Pi")

        @self.socketio.on('connect', namespace='/test')
        def test_connect():
            self.counter += 1
            print("Counter= {0}".format(self.counter))
            print('Client connected')

        @self.socketio.on('disconnect', namespace='/test')
        def test_disconnect():
            self.counter -= 1
            print("Counter= {0}".format(self.counter))
            print('Client disconnected')

        @self.socketio.on('getVersion', namespace='/test')
        def getversion():
            print('version')

        @self.socketio.on('ledRCtrl', namespace='/test')
        def ledrctrl(message):
            print(message['led'])
            GPIO.output(23, GPIO.HIGH if message['led'] else GPIO.LOW)

        self.socketio.run(app, host='0.0.0.0', port=5001)


    def background_thread(self):
        state = True
        while True:
            newstate = False if GPIO.input(18) else True
            if state != newstate:
                state = newstate
                print('Button', state)
                self.socketio.emit('but', {'state': state}, namespace='/test')
            time.sleep(.1)


if __name__ == '__main__':
    gui = WebApp()
