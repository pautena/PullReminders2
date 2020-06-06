import json

import pytest
import mongomock
from tests import MockResponse

from handlers import github_webhook


@pytest.fixture()
def initial_event():
    with open('tests/fixtures/hook_initial.json', 'r') as file:
        return {
            'body': json.dumps(json.loads(file.read()))
        }


@pytest.fixture()
def request_review_event():
    with open('tests/fixtures/hook_request_review.json', 'r') as file:
        return {
            'body': json.dumps(json.loads(file.read()))
        }


@pytest.fixture()
def request_changes_event():
    with open('tests/fixtures/hook_request_changes.json', 'r') as file:
        return {
            'body': json.dumps(json.loads(file.read()))
        }


@pytest.fixture()
def comment_event():
    with open('tests/fixtures/hook_comment.json', 'r') as file:
        return {
            'body': json.dumps(json.loads(file.read()))
        }


@pytest.fixture()
def accept_revision_event():
    with open('tests/fixtures/hook_accept_revision.json', 'r') as file:
        return {
            'body': json.dumps(json.loads(file.read()))
        }


@pytest.fixture()
def create_comment_event():
    with open('tests/fixtures/hook_response_comment.json', 'r') as file:
        body = json.loads(file.read())
        del body["comment"]["in_reply_to_id"]
        return {
            'body': json.dumps(body)
        }


@pytest.fixture()
def repply_comment_event():
    with open('tests/fixtures/hook_response_comment.json', 'r') as file:
        return {
            'body': json.dumps(json.loads(file.read()))
        }


def test_hook_initial_request(initial_event):

    ret = github_webhook.lambda_handler(initial_event, "")

    assert ret["statusCode"] == 200
    assert ret["body"] == 'ok'


def test_hook_request_revision_request(request_review_event, mocker):

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
        'pull_request': 425445400}


def test_hook_request_revision_request_review_exists(
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


def test_hook_accept_revision_request_request(accept_revision_event, mocker):
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

    ret = github_webhook.lambda_handler(accept_revision_event, "")

    assert ret["statusCode"] == 200
    assert ret["body"] == 'ok'

    mock_post.assert_called_with(
        'https://slack.com/api/chat.update',
        json.dumps(
            {
                'channel': 'faf3as',
                "ts": "111111",
                'text': '~user2 requested your review on [testrepo#2]~',
                "unfurl_links": False,
                "unfurl_media": False,
            }),
        headers={
            'Authorization': f'Bearer asdfasdfae3fasfas',
            "Content-Type": "application/json"})


def test_hook_accept_revision_request_non_existing_request(
        accept_revision_event, mocker):
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

    ret = github_webhook.lambda_handler(accept_revision_event, "")

    assert ret["statusCode"] == 200
    assert ret["body"] == 'ok'

    mock_post.assert_not_called()


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


def test_hook_create_comment_request_with_repply(repply_comment_event, mocker):
    review_requests_collection = mongomock.MongoClient().db.collection

    mocker.patch(
        'repository._get_review_requests_collection',
        return_value=review_requests_collection)

    user_collection = mongomock.MongoClient().db.collection

    user_collection.insert_one({
        "_id": 123433,
        "slack": {
            "user_id": "faf3as",
            "user_name": "user1",
            "response_url": "https://hooks.slack.com/commands/asdfasdf/asfasdf/qweqf",
            "team_domain": "test"
        },
        "github": {
            "id": 123433,
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

    comment_collection.insert_one({
        '_id': '425445400:9282348923',
        'comment_id': 9282348923,
        'body': 'original message',
        'user_id': 123433,
        'user_name': 'user1',
        'pull_request': 425445400
    })

    mocker.patch(
        'repository._get_comment_collection',
        return_value=comment_collection)

    slack_response = {
        'ts': '111111',
        'channel': 'faf3as'
    }
    mock_post = mocker.patch('requests.post', return_value=MockResponse(
        200, json.dumps(slack_response)))

    ret = github_webhook.lambda_handler(repply_comment_event, "")

    assert ret["statusCode"] == 200
    assert ret["body"] == 'ok'

    assert comment_collection.count_documents({}) == 2

    cursor = comment_collection.find()
    assert cursor[1] == {
        '_id': '425445400:432885618',
        'comment_id': 432885618,
        'body': 'aas',
        'user_id': 5763345,
        'user_name': 'user2',
        'pull_request': 425445400
    }
    mock_post.assert_called_with(
        'https://slack.com/api/chat.postMessage',
        json.dumps(
            {
                'channel': 'faf3as',
                # pylint: disable=C0301
                'text': 'user2 repplied to you in [testrepo#2] <https://github.com/user1/testrepo/pull/2#discussion_r432885618|WIP>',
                "unfurl_links": False,
                "unfurl_media": False,
                "attachments": [{
                    "color": "#355C7D",
                    "text": "user2: aas"
                }]
            }),
        headers={
            'Authorization': f'Bearer asdfasdfae3fasfas',
            "Content-Type": "application/json"}
    )
