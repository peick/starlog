import logging

from flask import Flask

app = Flask(__name__)

_log = logging.getLogger('app')


@app.route("/")
def hello():
    _log.info('incoming request')
    return "Hello World!"


if __name__ != '__main__':
    _log.info('my app is starting')
