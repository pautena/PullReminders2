
from slack import send_message


class BaseAction:
    def __init__(self, action):
        self.action = action

    def get_name(self):
        self.get_param('action')

    def get_param(self, param):
        return self.action.get(param, None)

    def __call__(self):
        pass

    # pylint: disable=W0102,R0201
    def send_message(self, message, user_id, attachments=[]):
        return send_message(message, user_id, attachments=attachments)


class NotFound(BaseAction):
    def __call__(self):
        print("NotFound")
        return f"Action {self.get_name()} not found"
