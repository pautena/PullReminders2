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


@pytest.fixture()
def repply_comment_event():
    with open('tests/fixtures/hook_response_comment.json', 'r') as file:
        return {
            'body': json.dumps(json.loads(file.read()))
        }


@pytest.fixture()
def submit_comment_event():
    with open('tests/fixtures/hook_submit_comment.json', 'r') as file:
        return {
            'body': json.dumps(json.loads(file.read()))
        }


@pytest.fixture()
def submit_comment_body_null_event():
    with open('tests/fixtures/hook_submit_comment_body_null.json', 'r') as file:
        return {
            'body': json.dumps(json.loads(file.read()))
        }


@pytest.fixture()
def submit_comment_owner_event():
    with open('tests/fixtures/hook_submit_comment_owner.json', 'r') as file:
        return {
            'body': json.dumps(json.loads(file.read()))
        }


@pytest.fixture()
def issue_comment_event():
    with open('tests/fixtures/hook_issue_comment.json', 'r') as file:
        return {
            'body': json.dumps(json.loads(file.read()))
        }


@pytest.fixture()
def issue_bot_comment_event():
    with open('tests/fixtures/hook_issue_comment_bot.json', 'r') as file:
        return {
            'body': json.dumps(json.loads(file.read()))
        }


@pytest.fixture()
def issue_owner_comment_event():
    with open('tests/fixtures/hook_issue_comment_owner.json', 'r') as file:
        return {
            'body': json.dumps(json.loads(file.read()))
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
        'user_id': 5763345,
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
        'user_id': 123433,
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
        'user_id': 5763345,
        'pull_request': 425445400
    }
    mock_post.assert_called_with(
        'https://slack.com/api/chat.postMessage',
        json.dumps(
            {
                'channel': 'faf3as',
                # pylint: disable=C0301
                'text': 'user2 repplied to you in [testrepo#2] <https://github.com/user1/testrepo/pull/2#xxx|WIP>',
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


def test_hook_create_comment_request_with_repply_and_existing_repplier(
        repply_comment_event, mocker):
    review_requests_collection = mongomock.MongoClient().db.collection

    mocker.patch(
        'repository._get_review_requests_collection',
        return_value=review_requests_collection)

    user_collection = mongomock.MongoClient().db.collection

    user_collection.insert_many([{
        "_id": 123433,
        "slack": {
            "user_id": "user1ID",
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
            "name": "User 2 Name",
            "access_token": "ahtawtewerg",
            "refresh_token": "anshttsetges"
        }
    }])

    mocker.patch(
        'repository._get_users_collection',
        return_value=user_collection)

    comment_collection = mongomock.MongoClient().db.collection

    comment_collection.insert_one({
        '_id': '425445400:9282348923',
        'comment_id': 9282348923,
        'user_id': 123433,
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
        'user_id': 5763345,
        'pull_request': 425445400
    }
    mock_post.assert_called_with(
        'https://slack.com/api/chat.postMessage',
        json.dumps(
            {
                'channel': 'user1ID',
                # pylint: disable=C0301
                'text': '<@user2ID> repplied to you in [testrepo#2] <https://github.com/user1/testrepo/pull/2#xxx|WIP>',
                "unfurl_links": False,
                "unfurl_media": False,
                "attachments": [{
                    "color": "#355C7D",
                    "text": "<@user2ID>: aas"
                }]
            }),
        headers={
            'Authorization': f'Bearer asdfasdfae3fasfas',
            "Content-Type": "application/json"}
    )


def test_hook_submit_comment_request(submit_comment_event, mocker):
    review_requests_collection = mongomock.MongoClient().db.collection

    mocker.patch(
        'repository._get_review_requests_collection',
        return_value=review_requests_collection)

    user_collection = mongomock.MongoClient().db.collection

    user_collection.insert_many([{
        "_id": 1234,
        "slack": {
            "user_id": "user1ID",
            "user_name": "user1",
            "response_url": "https://hooks.slack.com/commands/asdfasdf/asfasdf/qweqf",
            "team_domain": "test"
        },
        "github": {
            "id": 1234,
            "user_name": "user1",
            "name": "User 1 Name",
            "access_token": "ahtawtewerg",
            "refresh_token": "anshttsetges"
        }
    }, {
        "_id": 9876,
        "slack": {
            "user_id": "user2ID",
            "user_name": "user2",
            "response_url": "https://hooks.slack.com/commands/asdfasdf/asfasdf/qweqf",
            "team_domain": "test"
        },
        "github": {
            "id": 9876,
            "user_name": "user2",
            "name": "User 2 Name",
            "access_token": "ahtawtewerg",
            "refresh_token": "anshttsetges"
        }
    }])

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

    ret = github_webhook.lambda_handler(submit_comment_event, "")

    assert ret["statusCode"] == 200
    assert ret["body"] == 'ok'

    assert comment_collection.count_documents({}) == 0

    mock_post.assert_called_with(
        'https://slack.com/api/chat.postMessage',
        json.dumps(
            {
                'channel': 'user1ID',
                # pylint: disable=C0301
                'text': '<@user2ID> commented on [testpull#9] <https://github.com/user2/testpull/pull/9#pullrequestreview-52345234|Update README2.md>',
                "unfurl_links": False,
                "unfurl_media": False,
                "attachments": [{
                    "color": "#355C7D",
                    "text": "<@user2ID>: hello world!"
                }]
            }),
        headers={
            'Authorization': f'Bearer asdfasdfae3fasfas',
            "Content-Type": "application/json"
        }
    )

def test_hook_submit_comment_body_null_request(submit_comment_body_null_event, mocker):
    review_requests_collection = mongomock.MongoClient().db.collection

    mocker.patch(
        'repository._get_review_requests_collection',
        return_value=review_requests_collection)

    user_collection = mongomock.MongoClient().db.collection

    user_collection.insert_many([{
        "_id": 1234,
        "slack": {
            "user_id": "user1ID",
            "user_name": "user1",
            "response_url": "https://hooks.slack.com/commands/asdfasdf/asfasdf/qweqf",
            "team_domain": "test"
        },
        "github": {
            "id": 1234,
            "user_name": "user1",
            "name": "User 1 Name",
            "access_token": "ahtawtewerg",
            "refresh_token": "anshttsetges"
        }
    }, {
        "_id": 9876,
        "slack": {
            "user_id": "user2ID",
            "user_name": "user2",
            "response_url": "https://hooks.slack.com/commands/asdfasdf/asfasdf/qweqf",
            "team_domain": "test"
        },
        "github": {
            "id": 9876,
            "user_name": "user2",
            "name": "User 2 Name",
            "access_token": "ahtawtewerg",
            "refresh_token": "anshttsetges"
        }
    }])

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

    ret = github_webhook.lambda_handler(submit_comment_body_null_event, "")

    assert ret["statusCode"] == 200
    assert ret["body"] == 'ok'

    assert comment_collection.count_documents({}) == 0

    mock_post.assert_not_called()


def test_hook_submit_comment_owner_request(submit_comment_owner_event, mocker):
    review_requests_collection = mongomock.MongoClient().db.collection

    mocker.patch(
        'repository._get_review_requests_collection',
        return_value=review_requests_collection)

    user_collection = mongomock.MongoClient().db.collection

    user_collection.insert_one({
        "_id": 1234,
        "slack": {
            "user_id": "user2ID",
            "user_name": "user2",
            "response_url": "https://hooks.slack.com/commands/asdfasdf/asfasdf/qweqf",
            "team_domain": "test"
        },
        "github": {
            "id": 1234,
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

    ret = github_webhook.lambda_handler(submit_comment_owner_event, "")

    assert ret["statusCode"] == 200
    assert ret["body"] == 'ok'

    assert comment_collection.count_documents({}) == 0

    mock_post.assert_not_called()


def test_hook_issue_comment_request(issue_comment_event, mocker):
    review_requests_collection = mongomock.MongoClient().db.collection

    mocker.patch(
        'repository._get_review_requests_collection',
        return_value=review_requests_collection)

    user_collection = mongomock.MongoClient().db.collection

    user_collection.insert_many([{
        "_id": 1234,
        "slack": {
            "user_id": "user1ID",
            "user_name": "user1",
            "response_url": "https://hooks.slack.com/commands/asdfasdf/asfasdf/qweqf",
            "team_domain": "test"
        },
        "github": {
            "id": 1234,
            "user_name": "user1",
            "name": "User 1 Name",
            "access_token": "ahtawtewerg",
            "refresh_token": "anshttsetges"
        }
    }, {
        "_id": 9876,
        "slack": {
            "user_id": "user2ID",
            "user_name": "user2",
            "response_url": "https://hooks.slack.com/commands/asdfasdf/asfasdf/qweqf",
            "team_domain": "test"
        },
        "github": {
            "id": 9876,
            "user_name": "user2",
            "name": "User 2 Name",
            "access_token": "ahtawtewerg",
            "refresh_token": "anshttsetges"
        }
    }])

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

    ret = github_webhook.lambda_handler(issue_comment_event, "")

    assert ret["statusCode"] == 200
    assert ret["body"] == 'ok'

    assert comment_collection.count_documents({}) == 0

    mock_post.assert_called_with(
        'https://slack.com/api/chat.postMessage',
        json.dumps(
            {
                'channel': 'user2ID',
                # pylint: disable=C0301
                'text': '<@user1ID> commented on [testpull#9] <https://github.com/user1/testpull/pull/9#issuecomment-640189447|Update README2.md>',
                "unfurl_links": False,
                "unfurl_media": False,
                "attachments": [{
                    "color": "#355C7D",
                    "text": "<@user1ID>: hello world 6"
                }]
            }),
        headers={
            'Authorization': f'Bearer asdfasdfae3fasfas',
            "Content-Type": "application/json"}
    )


def test_hook_issue_comment_by_bot_request(issue_bot_comment_event, mocker):
    review_requests_collection = mongomock.MongoClient().db.collection

    mocker.patch(
        'repository._get_review_requests_collection',
        return_value=review_requests_collection)

    user_collection = mongomock.MongoClient().db.collection

    user_collection.insert_many([{
        "_id": 1234,
        "slack": {
            "user_id": "user1ID",
            "user_name": "user1",
            "response_url": "https://hooks.slack.com/commands/asdfasdf/asfasdf/qweqf",
            "team_domain": "test"
        },
        "github": {
            "id": 1234,
            "user_name": "user1",
            "name": "User 1 Name",
            "access_token": "ahtawtewerg",
            "refresh_token": "anshttsetges"
        }
    }])

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

    ret = github_webhook.lambda_handler(issue_bot_comment_event, "")

    assert ret["statusCode"] == 200
    assert ret["body"] == 'ok'

    assert comment_collection.count_documents({}) == 0

    mock_post.assert_not_called()


def test_hook_issue_comment_by_owner_request(
        issue_owner_comment_event, mocker):
    review_requests_collection = mongomock.MongoClient().db.collection

    mocker.patch(
        'repository._get_review_requests_collection',
        return_value=review_requests_collection)

    user_collection = mongomock.MongoClient().db.collection

    user_collection.insert_many([{
        "_id": 1234,
        "slack": {
            "user_id": "user1ID",
            "user_name": "user1",
            "response_url": "https://hooks.slack.com/commands/asdfasdf/asfasdf/qweqf",
            "team_domain": "test"
        },
        "github": {
            "id": 1234,
            "user_name": "user1",
            "name": "User 1 Name",
            "access_token": "ahtawtewerg",
            "refresh_token": "anshttsetges"
        }
    }, {
        "_id": 9876,
        "slack": {
            "user_id": "user2ID",
            "user_name": "user2",
            "response_url": "https://hooks.slack.com/commands/asdfasdf/asfasdf/qweqf",
            "team_domain": "test"
        },
        "github": {
            "id": 9876,
            "user_name": "user2",
            "name": "User 2 Name",
            "access_token": "ahtawtewerg",
            "refresh_token": "anshttsetges"
        }
    }])

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

    ret = github_webhook.lambda_handler(issue_owner_comment_event, "")

    assert ret["statusCode"] == 200
    assert ret["body"] == 'ok'

    assert comment_collection.count_documents({}) == 0

    mock_post.assert_not_called()
