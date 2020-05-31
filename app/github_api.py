import requests
import settings

def get_repos():
    r = requests.get('https://github.com/timeline.json')

    if r.status_code == 200:
        return r.json()
    return None

def get_access_token(code,state):
    body = {
        'client_id':settings.CLIENT_ID,
        'client_secret':settings.CLIENT_SECRET,
        'code':code,
        'redirect_uri':settings.OAUTH_REDIRECT_URL,
        'state':state,
    }
    r = requests.post("https://github.com/login/oauth/access_token",body)

    if r.status_code == 200:
        return r.text
    return None

def get_authenticated_profile(auth_token,owner,repo,comment_id):
    headers =  {
        "Authorization":f"token {auth_token}"
    }
    r = requests.get("https://api.github.com/repos/{owner}/{repo}/comments/{comment_id}",headers=headers)
    print(f"get_authenticated_profile -> code: {r.status_code}")

    if r.status_code == 200:
        return r.json()
    return None
