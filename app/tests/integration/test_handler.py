import json

import pytest
import mongomock
from mock import call
from tests import MockResponse

from handlers import commands, oauth_callback


@pytest.fixture()
def auth_event():
    return {
        # pylint: disable=C0301
        'body': 'command=auth&user_id=1234&user_name=pullrequets&token=asdf&response_url=https://example.com/response&team_domain=pull-team'
    }


@pytest.fixture()
def oauth_callback_event():
    return {
        "queryStringParameters": {
            "code": "random-code",
            "state": "random-state"
        }
    }


def test_command_auth_handler(auth_event, mocker):
    collection = mongomock.MongoClient().db.collection

    mocker.patch(
        'repository._get_oauth_collection',
        return_value=collection)
    mocker.patch(
        'repository._generate_state',
        return_value='random-state')

    ret = commands.lambda_handler(auth_event, "")

    assert ret["statusCode"] == 200
    # pylint: disable=C0301
    assert ret["body"] == "Click to this link https://github.com/login/oauth/authorize?client_id=asdf&redirect_uri=https://example.com/Prod/oauth/callback&state=random-state to authenticate"
    assert collection.count_documents({}) == 1

    cursor = collection.find()
    print(cursor[0])
    assert cursor[0] == {
        '_id': 'random-state',
        'state': 'random-state',
        'slack': {
            'user_id': '1234',
            'user_name': 'pullrequets',
            'token': 'asdf',
            'response_url': 'https://example.com/response',
            'team_domain': 'pull-team'
        }
    }


def test_oauth_callback_handler(oauth_callback_event, mocker):
    oauth_collection = mongomock.MongoClient().db.collection
    oauth_collection.insert_one({
        '_id': 'random-state',
        'state': 'random-state',
        'slack': {
            'user_id': '1234',
            'user_name': 'pullreq',
            'token': 'zzzzz',
            'response_url': 'https://example.com',
            'team_domain': 'pull-domain'
        }
    })

    mocker.patch(
        'repository._get_oauth_collection',
        return_value=oauth_collection)

    user_collection = mongomock.MongoClient().db.collection

    mocker.patch(
        'repository._get_users_collection',
        return_value=user_collection)

    profile = {
        "id": "profile-id",
        "login": "pull-r",
        "name": "Pull Reminders"
    }

    mock_post = mocker.patch('requests.post', return_value=MockResponse(
        200, "access_token=random-acess-token&refresh_token=asdf"))
    mocker.patch(
        'requests.get',
        return_value=MockResponse(
            200,
            json.dumps(profile)))

    ret = oauth_callback.lambda_handler(oauth_callback_event, "")

    assert ret["statusCode"] == 200

    body = json.loads(ret["body"])
    assert body["_id"] == "profile-id"
    assert 'slack' in body
    assert "github" in body

    assert user_collection.count_documents({}) == 1

    cursor = user_collection.find()
    assert cursor[0] == {
        '_id': 'profile-id',
        'slack': {
            'user_id': '1234',
            'user_name': 'pullreq',
            'response_url': 'https://example.com',
            'team_domain': 'pull-domain'
        },
        'github': {
            'id': 'profile-id',
            'user_name': 'pull-r',
            'name': 'Pull Reminders',
            'access_token': 'random-acess-token',
            'refresh_token': 'asdf'
        }
    }

    call1 = call("https://github.com/login/oauth/access_token", {
        'client_id': 'asdf',
        'client_secret': 'afghahesgsegasfgaefa',
        'code': 'random-code',
        'redirect_uri': 'https://example.com/Prod/oauth/callback',
        'state': 'random-state',
    })
    call2 = call('https://example.com', json.dumps({
        'text': 'Hello! Authentication success',
    }), headers={
        'Authorization': f'Bearer asdfasdfae3fasfas'
    })
    mock_post.assert_has_calls([call1, call2])
