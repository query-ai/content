import demistomock as demisto  # noqa: E402 lgtm [py/polluting-import]
from CommonServerUserPython import *  # noqa: E402 lgtm [py/polluting-import]
from CommonServerPython import *  # noqa: E402 lgtm [py/polluting-import]

from typing import Any, Dict
import urllib3
import urllib.parse

# Disable insecure warnings
urllib3.disable_warnings()


class Client(BaseClient):   # type: ignore

    def __init__(self, base_url, verify=True, proxy=False, ok_codes=tuple(), headers=None, auth=None,
                 email=None, license_key=None, connection_params='{}', alias=None):
        super().__init__(base_url, verify, proxy, ok_codes, headers, auth)
        self._email = email
        self._license_key = license_key
        self.alias = alias
        self.connection_params = safe_load_json(connection_params) if connection_params else {}

    def queryai_http_request(self, method, url_suffix, json_data=None, params=None, data=None, **kwargs):
        if not json_data:
            json_data = {}
        json_data['email'] = self._email
        json_data['license_key'] = self._license_key

        return self._http_request(
            method=method,
            url_suffix=url_suffix,
            params=params,
            json_data=json_data,
            data=data,
            **kwargs
        )

    def run_query(self, query: str, connection_params: str = None, workflow_params: str = None, time_text: str = None,
                  alias: str = None) -> Dict[str, Any]:
        """Gets result from QueryAI for the given query

        :type query: ``str``
        :param query: Query to be run

        :type connection_params: ``str``
        :param connection_params: Connection parameters as Stringified JSON

        :type workflow_params: ``str``
        :param workflow_params: Workflow parameters as Stringified JSON

        :type time_text: ``str``
        :param time_text: Search time-period

        :type alias: ``str``
        :param alias: Platform alias name

        :return: dict containing the response from the API
        :rtype: ``Dict[str, Any]``
        """

        if workflow_params:
            workflow_params = safe_load_json(workflow_params)

        if connection_params:
            connection_params = safe_load_json(connection_params)
        else:
            connection_params = self.connection_params

        if not alias:
            alias = self.alias

        return self.queryai_http_request(
            method='POST',
            url_suffix='/query',
            json_data={
                'query': query,
                'connection_params': connection_params,
                'workflow_params': workflow_params,
                'time_text': time_text,
                'alias': alias
            }
        )


def generate_drilldown_url(query, alias, time_text=None, workflow_params=None):
    base_drilldown = 'https://ai.query.ai/login;'
    questions_url_param = f'questions={urllib.parse.quote(query)};'
    alias_url_param = f'alias={urllib.parse.quote(alias)};'
    drilldown_url = base_drilldown + questions_url_param + alias_url_param

    if time_text:
        query_duration_url_param = f'queryDuration={urllib.parse.quote(time_text)};'
        drilldown_url += query_duration_url_param
    if workflow_params:
        workflow_params_url_param = f'params={urllib.parse.quote(workflow_params)};'
        drilldown_url += workflow_params_url_param

    return drilldown_url


def queryai_run_query_command(client: Client, args: Dict[str, Any]) -> CommandResults:
    """queryai-run-query command: Returns response for the query being run on QueryAI

    :type client: ``Client``
    :param client: QueryAI client to use

    :type args: ``Dict[str, Any]``
    :param args:
        all command arguments, usually passed from ``demisto.args()``.
        ``args['query']`` query to run

    :return:
        A ``CommandResults`` object that is then passed to ``return_results``,
        that contains an alert

    :rtype: ``CommandResults``
    """

    query = args.get('query', '')
    connection_params = args.get('connection_params', client.connection_params)
    workflow_params = args.get('workflow_params', None)
    time_text = args.get('time_text', None)
    alias = args.get('alias', client.alias)

    if not query:
        raise ValueError('Missing argument: "query"')

    result = client.run_query(query=query, connection_params=connection_params, workflow_params=workflow_params,
                              time_text=time_text, alias=alias)

    drilldown_url = f'### Click here to [see details]({generate_drilldown_url(query, alias, time_text, workflow_params)})'
    readable_output = tableToMarkdown(f'Query.AI Result for the query: {query}', result['data']) if result['data'] else ''
    readable_output += drilldown_url
    reply = {'result': result['data'] if result['data'] else result['reply'], 'markdown_string': readable_output}
    return CommandResults(
        readable_output=readable_output,
        outputs_prefix='QueryAI.query',
        outputs_key_field='',
        outputs=reply
    )


def test_module(client: Client) -> str:
    """Tests API connectivity and authentication'

    Returning 'ok' indicates that the integration works like it is supposed to.
    Connection to the service is successful.
    Raises exceptions if something goes wrong.

    :type client: ``Client``
    :param client: QueryAI client to use

    :return: 'ok' if test passed, anything else will fail the test.
    :rtype: ``str``
    """

    try:
        client.run_query(query='hello')
    except DemistoException as e:
        if 'Forbidden' in str(e):
            return 'Authorization Error: make sure License Key and Email is correctly set'
        else:
            raise e
    return 'ok'


def main() -> None:
    """main function, parses params and runs command functions

    :return:
    :rtype:
    """

    email = demisto.params().get('email')
    license_key = demisto.params().get('license_key')
    base_url = urljoin(demisto.params()['url'], '/api/v1')
    alias = demisto.params().get('alias')
    connection_params = demisto.params().get('connection_params', '{}')

    verify_certificate = not demisto.params().get('insecure', False)
    proxy = demisto.params().get('proxy', False)

    demisto.debug(f'Command being called is {demisto.command()}')
    try:
        headers = {}   # type:  Dict[str, str]
        client = Client(
            base_url=base_url,
            verify=verify_certificate,
            headers=headers,
            proxy=proxy,
            email=email,
            license_key=license_key,
            alias=alias,
            connection_params=connection_params,
        )

        if demisto.command() == 'test-module':
            # This is the call made when pressing the integration Test button.
            result = test_module(client)
            return_results(result)

        elif demisto.command() == 'queryai-run-query':
            return_results(queryai_run_query_command(client, demisto.args()))

        else:
            return_error(f'Unsupported Command: {demisto.command()}.\n')

    # Log exceptions and return errors
    except Exception as e:
        demisto.error(traceback.format_exc())  # print the traceback
        return_error(f'Failed to execute {demisto.command()} command.\nError:\n{str(e)}')


if __name__ in ('__main__', '__builtin__', 'builtins'):
    main()
