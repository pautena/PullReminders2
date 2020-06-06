import json

import pytest
import mongomock
from tests import MockResponse

from handlers import github_webhook


@pytest.fixture()
def request_review_event():
    with open('tests/fixtures/hook_request_review.json', 'r') as file:
        return {
            'body': json.dumps(json.loads(file.read()))
        }


def test_hook_request_review_request(request_review_event, mocker):

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

    ret = github_webhook.lambda_handler(request_review_event, "")

    assert ret["statusCode"] == 200
    assert ret["body"] == 'ok'

    mock_post.assert_called_with('https://slack.com/api/chat.postMessage', json.dumps({
        'channel': 'faf3as',
        # pylint: disable=C0301
        'text': 'user2 requested your review on [testrepo#2] <https://github.com/user1/testrepo/pull/2|WIP>',
        "unfurl_links": False,
        "unfurl_media": False,
        "attachments": []
    }), headers={
        'Authorization': f'Bearer asdfasdfae3fasfas',
        "Content-Type": "application/json"
    })

    assert review_requests_collection.count_documents({}) == 1
    cursor = review_requests_collection.find()
    assert cursor[0] == {
        '_id': '425445400:3452345',
        'ts': '111111',
        'channel': 'faf3as',
        # pylint: disable=C0301
        'message': 'user2 requested your review on [testrepo#2] <https://github.com/user1/testrepo/pull/2|WIP>',
        'user': 3452345,
        'pull_request': 425445400
    }


def test_hook_request_review_requester_exists_request(
        request_review_event, mocker):

    review_requests_collection = mongomock.MongoClient().db.collection

    mocker.patch(
        'repository._get_review_requests_collection',
        return_value=review_requests_collection)

    user_collection = mongomock.MongoClient().db.collection

    user_collection.insert_many([{
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
    }, {
        "_id": 5763345,
        "slack": {
            "user_id": "user2ID",
            "user_name": "user2",
            "response_url": "https://hooks.slack.com/commands/asdfasdf/asfasdf/qweqf",
            "team_domain": "test"
        },
        "github": {
            "id": 5763345,
            "user_name": "user2",
            "name": "User 1 Name",
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

    ret = github_webhook.lambda_handler(request_review_event, "")

    assert ret["statusCode"] == 200
    assert ret["body"] == 'ok'

    mock_post.assert_called_with('https://slack.com/api/chat.postMessage', json.dumps({
        'channel': 'faf3as',
        # pylint: disable=C0301
        'text': '<@user2ID> requested your review on [testrepo#2] <https://github.com/user1/testrepo/pull/2|WIP>',
        "unfurl_links": False,
        "unfurl_media": False,
        "attachments": []
    }), headers={
        'Authorization': f'Bearer asdfasdfae3fasfas',
        "Content-Type": "application/json"
    })

    assert review_requests_collection.count_documents({}) == 1
    cursor = review_requests_collection.find()
    assert cursor[0] == {
        '_id': '425445400:3452345',
        'ts': '111111',
        'channel': 'faf3as',
        # pylint: disable=C0301
        'message': '<@user2ID> requested your review on [testrepo#2] <https://github.com/user1/testrepo/pull/2|WIP>',
        'user': 3452345,
        'pull_request': 425445400
    }


def test_hook_request_review_request_review_exists(
        request_review_event, mocker):

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

    ret = github_webhook.lambda_handler(request_review_event, "")

    assert ret["statusCode"] == 200
    assert ret["body"] == 'ok'

    mock_post.assert_called_with('https://slack.com/api/chat.update', json.dumps({
        'channel': 'faf3as',
        "ts": "111111",
        # pylint: disable=C0301
        'text': 'user2 requested your review on [testrepo#2] <https://github.com/user1/testrepo/pull/2|WIP>',
        "unfurl_links": False,
        "unfurl_media": False,
    }), headers={
        'Authorization': f'Bearer asdfasdfae3fasfas',
        "Content-Type": "application/json"
    })
