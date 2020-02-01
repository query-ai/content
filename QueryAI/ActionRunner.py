import json
from QueryAI import queryaiDemistomock as demisto
from Integrations.JiraV2 import JiraV2 as jira

def run_action(action):
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
    demisto.reset()
    demisto.setCommand(action['command'])
    demisto.setRequestId(action['request_id'])
    for paramKey, paramVal in action['params'].items():
        demisto.setParam(paramKey, paramVal)
    for argKey, argVal in action['args'].items():
        demisto.setArg(argKey, argVal)

    # Command syntax is usually 'platformName-specificCommand'
    if action['command'].startswith('jira'):
        return jira.run_jira_command()

def getResult(request_id):
    """
    Method to get result from log file

    :param request_id: Request Id of the request whose result is to be fetched
    :type request_id: ``str``

    :rtype: ``dict``
    """
    try:
        json_file = open('results.json', 'r')
        results = json.load(json_file)
        return results[request_id]
    except:
        return

if __name__ == '__main__':
    ## ------ Mock Data ----- ##
    action = {
        'request_id': 'abc1234',
        'command': 'jira-get-issue',
        'params': {
            "url": "https://something.atlassian.net/",
            "username": "abc@xyz.com",
            "APItoken": "xxxxx"
        },
        'args': {
            'issue_id':'pqr-1234'
        }

    }
    ## ----------------------- ##
    run_action(action)

    # Print logged result to console
    print(json.dumps(getResult('abc1234'), indent=4, sort_keys=True))
