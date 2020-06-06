import requests
import settings


def get_repos():
    response = requests.get('https://github.com/timeline.json')

    if response.status_code == 200:
        return response.json()
    return None


def get_access_token(code, state):
    body = {
        'client_id': settings.CLIENT_ID,
        'client_secret': settings.CLIENT_SECRET,
        'code': code,
        'redirect_uri': settings.OAUTH_REDIRECT_URL,
        'state': state,
    }
    response = requests.post(
        "https://github.com/login/oauth/access_token", body)

    if response.status_code == 200:
        return response.text
    return None


def get_authenticated_profile(auth_token):
    headers = {
        "Authorization": f"token {auth_token}"
    }
    response = requests.get("https://api.github.com/user", headers=headers)
    print(f"get_authenticated_profile -> code: {response.status_code}")

    if response.status_code == 200:
        return response.json()
    return None
