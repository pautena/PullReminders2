
import settings


def get_oauth_login_url(state):
    # pylint: disable=C0301
    return f'{settings.BASE_URL}?client_id={settings.CLIENT_ID}&redirect_uri={settings.OAUTH_REDIRECT_URL}&state={state}'
