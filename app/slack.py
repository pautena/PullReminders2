import json
import requests
import settings


def send_response_via_hook(message, hook_url):
    print(
        f"send_response_via_hook -> message: {message}, hook_url: {hook_url}")

    headers = {
        'Authorization': f'Bearer {settings.SLACK_BOT_ACCESS_TOKEN}'
    }
    body = json.dumps({
        'text': message
    })
    response = requests.post(hook_url, body, headers=headers)
    print(
        f"send_response_via_hook -> status_code: {response.status_code}, text: {response.text}")
    if response.status_code == 200:
        return response.text
    return None


# pylint: disable=W0102
def send_message(message, user_id, attachments=[]):
    print(f"send_message -> message: {message}, user_id: {user_id}")

    headers = {
        'Authorization': f'Bearer {settings.SLACK_BOT_ACCESS_TOKEN}',
        "Content-Type": "application/json"
    }
    body = {
        'channel': user_id,
        'text': message,
        "unfurl_links": False,
        "unfurl_media": False,
        "attachments": attachments
    }
    print("body: ", body)

    response = requests.post(
        'https://slack.com/api/chat.postMessage',
        json.dumps(body),
        headers=headers)
    print(
        f"send_message -> status_code: {response.status_code}, text: {response.text}")
    if response.status_code == 200:
        return response.json()
    return None


def update_message(message, timestamp, user_id):
    print(f"update_message -> message: {message}, ts: {timestamp}")

    headers = {
        'Authorization': f'Bearer {settings.SLACK_BOT_ACCESS_TOKEN}',
        "Content-Type": "application/json"
    }
    body = {
        'channel': user_id,
        'ts': timestamp,
        'text': message,
        "unfurl_links": False,
        "unfurl_media": False
    }
    response = requests.post(
        'https://slack.com/api/chat.update',
        json.dumps(body),
        headers=headers)
    print(
        f"update_message -> status_code: {response.status_code}, text: {response.text}")
    if response.status_code == 200:
        return response.json()
    return None
