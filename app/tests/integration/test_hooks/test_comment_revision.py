import json

import pytest
import mongomock
from tests import MockResponse

from handlers import github_webhook


@pytest.fixture()
def comment_event():
    with open('tests/fixtures/hook_comment.json', 'r') as file:
        return {
            'body': json.dumps(json.loads(file.read()))
        }


def test_comment_revision_request(comment_event, mocker):
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

    ret = github_webhook.lambda_handler(comment_event, "")

    assert ret["statusCode"] == 200
    assert ret["body"] == 'ok'

    mock_post.assert_not_called()
