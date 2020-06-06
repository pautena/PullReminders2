import json


import sentry
sentry.initialize()

# pylint: disable=W0613,W0105


def lambda_handler(event, context):

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "hello world",
            # "location": ip.text.replace("\n", "")
        }),
    }
