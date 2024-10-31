import json
import random
import urllib.request
import urllib.error
import logging

logger = logging.getLogger("django")


def json_rpc(url, method, params):
    data = {
        "jsonrpc": "2.0",
        "method": method.lower(),
        "params": params,
        "id": random.randint(0, 1000000000),
    }
    req = urllib.request.Request(url=url, data=json.dumps(data).encode(), headers={
        "Content-Type": "application/json"
    })
    response = urllib.request.urlopen(req)
    reply = json.loads(response.read().decode('UTF-8'))
    if 'error' in reply:
        logger.error(f"Error: {reply['error']}")
        raise Exception(reply['error'])
    return reply['result']


def call(url, service, method, *args):
    return json_rpc(url, "call", {"service": service, "method": method, "args": args})


def call_kw(url, cred, model, method, domain_list, limit):
    return json_rpc(url, "call", {
        "service": "object",
        "method": "execute_kw",
        "args": [*cred, model, method, domain_list, limit]
    })