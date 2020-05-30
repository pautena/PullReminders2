import urllib.parse
from .implementation import get_action


def run_hook_action(action):
    return get_action(action['action'])(action)()
