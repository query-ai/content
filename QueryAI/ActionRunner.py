import json
from redis import Redis
import demistomock as demisto
import os
import re

redis = Redis(host='localhost', port=6389, decode_responses=True)

def run_action():
    """
    Method to run a given action

    action = {
        'request_id': '',
        'command': '',
        'params': {},
        'args': {}
    }

    :param action: action to be run
    :type action: ``dict``

    :return: None
    :rtype: ``None``
    """
    request_id = os.getcwd().split('/')[-1]
    if not redis.exists(request_id):
        redis.hmset(request_id, {'status': 'ERROR', 'response': 'Invalid job Id'})
    try:
        pid = os.getpid()
        redis.hmset(request_id, { 'pid': pid })
        demisto.reset()
        demisto.setCommand(redis.hget(request_id, 'command'))
        demisto.setRequestId(redis.hget(request_id, 'request_id'))
        params = redis.hget(request_id, 'params')
        if params:
            params = json.loads(params)
        else:
            params = {}
        args = redis.hget(request_id, 'args')
        if args:
            args = json.loads(args)
        else:
            args = {}
        platform = redis.hget(request_id, 'platform')
        if not platform:
            raise RuntimeError('platform is not defined while running query')
        for paramKey, paramVal in params.items():
            demisto.setParam(paramKey, paramVal)
        for argKey, argVal in args.items():
            demisto.setArg(argKey, argVal)
        open('CommonServerUserPython.py', 'a').close()  # create empty file
        integration_file = platform + '.py'
        with open(integration_file) as f:
            code = compile(f.read(), integration_file, 'exec')
            redis.hmset(request_id, {'status': 'INPROGRESS', 'response': ''})
            exec(code, globals())
    except Exception as err:
        if redis.exists(request_id):
            redis.hmset(request_id, {'status': 'ERROR', 'response': str(err)})

if __name__ == '__main__':
    ## ------ Mock Data ----- ##
    '''
    params = {
            "url": "https://api.crowdstrike.com",
            "client_id": "6b87a573590441b48684a7f6bc604252",
            "secret": "xL5oepqY2Nj98W30Pi7H6VrsGvgZkOICcfyX41bA"
        }
    action = {
        'request_id': '1c8784e0-c8ec-4a69-aa12-c3f5bb697e62',
        'command': 'cs-falcon-search-device',
        'params':  json.dumps(params),
        'platform': 'CrowdStrikeFalcon'
    }
    redis.hmset(action['request_id'], action)
    '''
    ## ----------------------- ##
    run_action()
