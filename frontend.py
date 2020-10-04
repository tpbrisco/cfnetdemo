from flask import Flask, jsonify, request
from werkzeug.routing import Rule
from optparse import OptionParser
from pprint import pprint
import time
import os
import socket
import requests

VERBOSE = 'verbose'
REMOTE_NEIGHBOR = 'remote_neighbor'
REMOTE_PORT = 'remote_port'

config = {
    VERBOSE: False,
}

app = Flask(__name__)

app.url_map.add(Rule('/', defaults={'path': ''}, endpoint='index'))
app.url_map.add(Rule('/<path:path>', endpoint='index'))


def extract(d):
    return {key: value for (key, value) in d.items()}


def neighbor():

    # get address for information purposes
    try:
        addr = socket.gethostbyname(config[REMOTE_NEIGHBOR])
        print("Fetching neighbor at {}:{} ({})".format(config[REMOTE_NEIGHBOR],
                                                       config[REMOTE_PORT],
                                                       addr))
    except socket.gaierror as e:
        status_code = 500
        return_data = str(e)
        return {'status': status_code,
                'neighbor_url': 'http://{}:{}'.format(config[REMOTE_NEIGHBOR],
                                                      config[REMOTE_PORT]),
                'error': return_data}

    try:
        r = requests.get('http://{}:{}'.format(config[REMOTE_NEIGHBOR],
                                               config[REMOTE_PORT]))
        status_code = r.status_code
        return_data = r.json()
    except requests.exceptions.RequestException as e:
        status_code = 500
        return_data = str(e)

    data = {
        'status': status_code,
        'neighbor_url': 'http://{}:{}'.format(config[REMOTE_NEIGHBOR],
                                              config[REMOTE_PORT]),
        'neighbor': return_data
    }
    return data


@app.endpoint('index')
def echo(path):
    status_code = request.args.get('status') or 200
    status_code = int(status_code)

    data = {
        'success': True,
        'status': status_code,
        'time': time.time(),
        'path': request.path,
        'script_root': request.script_root,
        'url': request.url,
        'base_url': request.base_url,
        'url_root': request.url_root,
        'method': request.method,
        'headers': extract(request.headers),
        'data': request.data.decode(encoding='UTF-8'),
        'host': request.host,
        'args': extract(request.args),
        'form': extract(request.form),
        'json': request.json,
        'cookies': extract(request.cookies),
        'remote_neighbor': config[REMOTE_NEIGHBOR],
        'remote_port': config[REMOTE_PORT]
    }
    if request.path == '/neighbor':
        data['remote_data'] = neighbor()

    if config[VERBOSE]:
        pprint(data)

    response = jsonify(data)
    response.status_code = status_code
    return response


def main():
    parser = OptionParser()
    parser.add_option('--port', dest='port', default=5000,
                      help='port to run server on (default: 5000)')
    parser.add_option('--host', dest='host', default='127.0.0.1',
                      help='host to bind server on (default: 127.0.0.1)')
    parser.add_option('-v', '--verbose', dest='verbose', default=False,
                      action='store_true',
                      help='verbosity (outputs to console)')
    parser.add_option('--debug', dest='debug', default=False,
                      action='store_true',
                      help='enable debug mode in flask')
    parser.add_option('-remote', dest='remote_neighbor', default='',
                      help='remote host to fetch data from')
    parser.add_option('--remote-port', dest='remote_port', default=5000,
                      help='remote host port (default=5000)')
    (options, args) = parser.parse_args()

    config[VERBOSE] = options.verbose

    app.debug = options.debug
    app.run(port=int(options.port), host=options.host)


config[REMOTE_NEIGHBOR] = os.getenv('REMOTE_NEIGHBOR', default='')
config[REMOTE_PORT] = int(os.getenv('REMOTE_PORT', default='5000'))


if __name__ == '__main__':
    main()
