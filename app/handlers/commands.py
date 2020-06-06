
import sentry
# pylint: disable=C0411
from commands import run_command
from . import parse_command_body

sentry.initialize()

# pylint: disable=W0613,W0105


def lambda_handler(event, context):
    command = parse_command_body(event["body"])

    response = "parse error"
    if command['command']:
        response = run_command(command)

    return {
        "statusCode": 200,
        "body": response,
    }
