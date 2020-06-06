import urllib.parse
from .implementation import ReviewRequestedAction, SubmitReviewAction, CreatedAction, ClosedAction
from .base import NotFound


ACTIONS = {
    'review_requested': ReviewRequestedAction,
    'submitted': SubmitReviewAction,
    'created': CreatedAction,
    'closed': ClosedAction
}


def get_action(action):
    if action in ACTIONS:
        return ACTIONS[action]
    return NotFound


def run_hook_action(action):
    return get_action(action['action'])(action)()
