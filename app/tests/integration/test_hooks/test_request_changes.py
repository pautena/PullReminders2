import json

import pytest
import mongomock
from tests import MockResponse

from handlers import github_webhook


@pytest.fixture()
def request_changes_event():
    with open('tests/fixtures/hook_request_changes.json', 'r') as file:
        return {
            'body': json.dumps(json.loads(file.read()))
        }


def test_request_changes_revision_request(request_changes_event, mocker):
    review_requests_collection = mongomock.MongoClient().db.collection

    review_requests_collection.insert_one({
        '_id': '425445400:3452345',
        'ts': '111111',
        'channel': 'faf3as',
        'message': 'user2 requested your review on [testrepo#2]',
        'user': 3452345,
        'pull_request': 425445400
    })

    mocker.patch(
        'repository._get_review_requests_collection',
        return_value=review_requests_collection)

    user_collection = mongomock.MongoClient().db.collection

    user_collection.insert_one({
        "_id": 3452345,
        "slack": {
            "user_id": "faf3as",
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
    })

    mocker.patch(
        'repository._get_users_collection',
        return_value=user_collection)

    slack_response = {
        'ts': '111111',
        'channel': 'faf3as'
    }
    mock_post = mocker.patch('requests.post', return_value=MockResponse(
        200, json.dumps(slack_response)))

    ret = github_webhook.lambda_handler(request_changes_event, "")

    assert ret["statusCode"] == 200
    assert ret["body"] == 'ok'

    mock_post.assert_called_with(
        'https://slack.com/api/chat.update',
        json.dumps(
            {
                'channel': 'faf3as',
                "ts": "111111",
                'text': 'user2 requested your review on [testrepo#2]',
                "unfurl_links": False,
                "unfurl_media": False,
            }),
        headers={
            'Authorization': f'Bearer asdfasdfae3fasfas',
            "Content-Type": "application/json"})


def test_hook_request_changes_request_non_existing_request(
        request_changes_event, mocker):
    review_requests_collection = mongomock.MongoClient().db.collection

    mocker.patch(
        'repository._get_review_requests_collection',
        return_value=review_requests_collection)

    user_collection = mongomock.MongoClient().db.collection

    user_collection.insert_one({
        "_id": 3452345,
        "slack": {
            "user_id": "faf3as",
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
    })

    mocker.patch(
        'repository._get_users_collection',
        return_value=user_collection)

    slack_response = {
        'ts': '111111',
        'channel': 'faf3as'
    }
    mock_post = mocker.patch('requests.post', return_value=MockResponse(
        200, json.dumps(slack_response)))

    ret = github_webhook.lambda_handler(request_changes_event, "")

    assert ret["statusCode"] == 200
    assert ret["body"] == 'ok'

    mock_post.assert_not_called()
