import json
from repository import get_oauth_by_state
from github_api import get_access_token,get_authenticated_profile
from commands import parse_command_body
from repository import login_profile
from slack import send_response_via_hook

import sentry
sentry.initialize()


def lambda_handler(event, context):

    code = event["queryStringParameters"]["code"]
    state = event["queryStringParameters"]["state"]

    access_token = parse_command_body(get_access_token(code,state))
    oauth = get_oauth_by_state(state)
    profile = get_authenticated_profile(access_token['access_token'])

    print("oauth: ",oauth)
    print("access_token: ",access_token)
    print("profile: ",profile)

    can_login = profile and oauth and access_token
    user = None
    if can_login:
        user = login_profile(oauth,profile,access_token)
        msg="Hello! Authentication success"
    else:
        msg="Ops! Authentication fail"
    
    send_response_via_hook(msg,oauth['slack']['response_url'])

    return {
        "statusCode": 200,
        "body":json.dumps(user),
    }
