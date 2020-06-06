import json

import pytest
import mongomock
from tests import MockResponse

from handlers import github_webhook


@pytest.fixture()
def create_comment_event():
    with open('tests/fixtures/hook_response_comment.json', 'r') as file:
        body = json.loads(file.read())
        del body["comment"]["in_reply_to_id"]
        return {
            'body': json.dumps(body)
        }


def test_hook_create_comment_request(create_comment_event, mocker):
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

    comment_collection = mongomock.MongoClient().db.collection

    mocker.patch(
        'repository._get_comment_collection',
        return_value=comment_collection)

    slack_response = {
        'ts': '111111',
        'channel': 'faf3as'
    }
    mock_post = mocker.patch('requests.post', return_value=MockResponse(
        200, json.dumps(slack_response)))

    ret = github_webhook.lambda_handler(create_comment_event, "")

    assert ret["statusCode"] == 200
    assert ret["body"] == 'ok'

    mock_post.assert_not_called()
    assert comment_collection.count_documents({}) == 1

    cursor = comment_collection.find()
    assert cursor[0] == {
        '_id': '425445400:432885618',
        'comment_id': 432885618,
        'body': 'aas',
        'user_id': 5763345,
        'user_name': 'user2',
        'pull_request': 425445400
    }
