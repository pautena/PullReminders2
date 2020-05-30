import json
from commands import parse_command_body,run_command

import sentry
sentry.initialize()

def lambda_handler(event, context):
    command = parse_command_body(event["body"])

    response = "parse error"
    if command['command']:
        response = run_command(command)


    return {
        "statusCode": 200,
        "body": response,
    }
