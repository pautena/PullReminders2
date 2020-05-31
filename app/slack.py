
import requests
import settings
import json

def send_response_via_hook(message,hook_url):
    print(f"send_response_via_hook -> message: {message}, hook_url: {hook_url}")

    headers = {
        'Authorization':f'Bearer {settings.SLACK_BOT_ACCESS_TOKEN}'
    }
    body = json.dumps({
        'text':message
    })
    r = requests.post(hook_url,body,headers=headers)
    print(f"send_response_via_hook -> status_code: {r.status_code}, text: {r.text}")
    if r.status_code == 200:
        return r.text
    return None

def send_message(message,user_id,attachments=[]):
    print(f"send_message -> message: {message}, user_id: {user_id}")

    headers = {
        'Authorization':f'Bearer {settings.SLACK_BOT_ACCESS_TOKEN}',
        "Content-Type":"application/json"
    }
    body = {
        'channel':user_id,
        'text':message,
        "unfurl_links": False,
        "unfurl_media": False,
        "attachments": attachments
    }
    print("body: ",body)

    r = requests.post('https://slack.com/api/chat.postMessage',json.dumps(body),headers=headers)
    print(f"send_message -> status_code: {r.status_code}, text: {r.text}")
    if r.status_code == 200:
        return r.json()
    return None

def update_message(message,ts,user_id):
    print(f"update_message -> message: {message}, ts: {ts}")

    headers = {
        'Authorization':f'Bearer {settings.SLACK_BOT_ACCESS_TOKEN}',
        "Content-Type":"application/json"
    }
    body = {
        'channel':user_id,
        'ts':ts,
        'text':message,
        "unfurl_links": False,
        "unfurl_media": False
    }
    r = requests.post('	https://slack.com/api/chat.update',json.dumps(body),headers=headers)
    print(f"update_message -> status_code: {r.status_code}, text: {r.text}")
    if r.status_code == 200:
        return r.json()
    return None