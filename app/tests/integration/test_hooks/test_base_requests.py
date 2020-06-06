import json

import pytest

from handlers import github_webhook


@pytest.fixture()
def initial_event():
    with open('tests/fixtures/hook_initial.json', 'r') as file:
        return {
            'body': json.dumps(json.loads(file.read()))
        }


@pytest.fixture()
def non_existing_event(initial_event):
    initial_event["action"] = 'lorem-ipsum'
    return initial_event


def test_hook_initial_request(initial_event):

    ret = github_webhook.lambda_handler(initial_event, "")

    assert ret["statusCode"] == 200
    assert ret["body"] == 'ok'


def test_hook_non_existing_action_request(non_existing_event):

    ret = github_webhook.lambda_handler(non_existing_event, "")

    assert ret["statusCode"] == 200
    assert ret["body"] == 'ok'
