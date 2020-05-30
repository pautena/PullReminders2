import json
from hooks import run_hook_action

import sentry
sentry.initialize()


def lambda_handler(event, context):
    body = json.loads(event["body"])

    if body['action']:
        run_hook_action(body)


    return {
        "statusCode": 200,
        "body":'ok'
    }
