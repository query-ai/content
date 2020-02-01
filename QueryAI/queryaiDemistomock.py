import json
import logging
import uuid


''' Data Required by Integration Scripts '''
PARAMS = {}
COMMAND = ''
ARGS = {}
REQUEST_ID = ''

''' Methods to set/get PARAMS, ARGS, COMMAND'''
def getParam(param):
    return params().get(param)

def params():
    return PARAMS

def debug(*args):
    log(args)

def log(msg):
    logging.getLogger().info(msg)

def get(obj, field):
    """ Get the field from the given dict using dot notation """
    parts = field.split(".")
    for part in parts:
        if obj and part in obj:
            obj = obj[part]
        else:
            return None
    return obj

def gets(obj, field):
    return str(get(obj, field))

def incidents(incidents=None):
    """
    In integrations this is used to return incidents to the server

    Arguments:
        incidents {list with objects} -- List with incident objects

    Returns:
        [type] -- [description]
    """
    results(
        {"Type": 1, "Contents": json.dumps(incidents), "ContentsFormat": "json"}
    )


def results(results):
    if type(results) is dict and results.get("contents"):
        results = results.get("contents")
    log("demisto results: {}".format(json.dumps(results, indent=4, sort_keys=True)))
    try:
        json_file = open('results.json', 'r')
        request_results = json.load(json_file)
        json_file.close()
    except:
        request_results = {}
    with open('results.json', 'w') as json_file:
        request_results[REQUEST_ID] = results
        json_file.write(json.dumps(request_results, indent=4, sort_keys=True))

def command():
    return COMMAND

def args():
    return ARGS

def getArg(arg):
    return args().get(arg)

def getFilePath(id):
    return {'id': id, 'path': 'test/test.txt', 'name': 'test.txt'}

def getLastRun():
    return {"lastRun": "2018-10-24T14:13:20+00:00"}

def setLastRun(obj):
    return None

def uniqueFile():
    return str(uuid.uuid4())

def investigation():
    return {"id": "1"}

def setArg(argKey, argVal):
    args()[argKey] =  argVal

def setParam(paramKey, paramVal):
    params()[paramKey] = paramVal

def setCommand(command):
    global COMMAND
    COMMAND = command

def setRequestId(request_id):
    global REQUEST_ID
    REQUEST_ID = request_id

def reset():
    global COMMAND, ARGS, PARAMS, REQUEST_ID
    ARGS = {}
    PARAMS = {}
    COMMAND = ''
    REQUEST_ID = ''