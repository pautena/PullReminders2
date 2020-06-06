
import json

import pytest
import mongomock
from mock import call
from tests import MockResponse

from handlers import github_webhook


@pytest.fixture()
def close_event():
    with open('tests/fixtures/hook_close_pr.json', 'r') as file:
        return {
            'body': json.dumps(json.loads(file.read()))
        }


def test_close_pr(close_event, mocker):
    review_requests_collection = mongomock.MongoClient().db.collection

    review_requests_collection.insert_many([{
        '_id': '123412:3452345',
        'ts': '111111',
        'channel': 'chUser1',
        'message': 'user5 requested your review on [testrepo#2]',
        'user': 3452345,
        'pull_request': 123412
    }, {
        '_id': '123412:12345',
        'ts': '22222',
        'channel': 'chUser3',
        'message': 'user5 requested your review on [testrepo#2]',
        'user': 12345,
        'pull_request': 123412
    }, {
        '_id': '123412:412341234',
        'ts': '22222',
        'channel': 'chUser2',
        'message': 'user5 requested your review on [testrepo#2]',
        'user': 412341234,
        'pull_request': 123412
    }, ])

    mocker.patch(
        'repository._get_review_requests_collection',
        return_value=review_requests_collection)

    user_collection = mongomock.MongoClient().db.collection

    user_collection.insert_many([{
        "_id": 3452345,
        "slack": {
            "user_id": "user1id",
            "user_name": "user1",
            "response_url": "https://hooks.slack.com/commands/asdfasdf/asfasdf/qweqf",
            "team_domain": "test"
        },
        "github": {
            "id": 3452345,
            "user_name": "user1",
            "name": "User 1 Name",
            "access_token": "ahtawtewerg",
            "refresh_token": "anshttsetges"
        }
    }, {
        "_id": 412341234,
        "slack": {
            "user_id": "user2id",
            "user_name": "user2",
            "response_url": "https://hooks.slack.com/commands/asdfasdf/asfasdf/qweqf",
            "team_domain": "test"
        },
        "github": {
            "id": 412341234,
            "user_name": "user2",
            "name": "User 2 Name",
            "access_token": "ahtawtewerg",
            "refresh_token": "anshttsetges"
        }
    }])

    mocker.patch(
        'repository._get_users_collection',
        return_value=user_collection)

    slack_response = {
        'ts': '111111',
        'channel': 'faf3as'
    }
    mock_post = mocker.patch('requests.post', return_value=MockResponse(
        200, json.dumps(slack_response)))

    ret = github_webhook.lambda_handler(close_event, "")

    assert ret["statusCode"] == 200
    assert ret["body"] == 'ok'

    call2 = call('https://slack.com/api/chat.update', json.dumps({
        'channel': 'chUser2',
        'ts': '22222',
        'text': '~user5 requested your review on [testrepo#2]~',
        "unfurl_links": False,
        "unfurl_media": False
    }), headers={
        'Authorization': f'Bearer asdfasdfae3fasfas',
        "Content-Type": "application/json"
    })

    call1 = call('https://slack.com/api/chat.update', json.dumps({
        'channel': 'chUser1',
        'ts': '111111',
        'text': '~user5 requested your review on [testrepo#2]~',
        "unfurl_links": False,
        "unfurl_media": False
    }), headers={
        'Authorization': f'Bearer asdfasdfae3fasfas',
        "Content-Type": "application/json"
    })

    assert mock_post.call_count == 2
    mock_post.assert_has_calls([call1, call2])
