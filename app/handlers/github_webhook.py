import json
from hooks import run_hook_action

import sentry
sentry.initialize()

# pylint: disable=W0613,W0105


def lambda_handler(event, context):
    print(f'event: {event["body"]}')
    body = json.loads(event["body"])

    if 'action' in body and body['action']:
        run_hook_action(body)

    return {
        "statusCode": 200,
        "body": 'ok'
    }
