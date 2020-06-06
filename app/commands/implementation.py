from oauth import get_oauth_login_url
from repository import get_oauth_instance


class BaseCommand:
    def __init__(self, command):
        self.command = command

    def get_command_name(self):
        self.get_param('command')

    def get_args(self):
        self.get_param('args')

    def get_param(self, param):
        return self.command.get(param, None)

    def __call__(self):
        pass


class NotFound(BaseCommand):
    def __call__(self):
        print("NotFound")
        return f"Command {self.get_command_name()} not found"


class Authenticate(BaseCommand):
    def __call__(self):
        print("Authenticate")

        state = get_oauth_instance(
            self.get_param("user_id"),
            self.get_param("user_name"),
            self.get_param("token"),
            self.get_param("response_url"),
            self.get_param("team_domain")
        )

        url = get_oauth_login_url(state)
        return f'Click to this link {url} to authenticate'


class GetRepos(BaseCommand):
    def __call__(self):
        print("get repos")
        return "GetRepos -> not implemented yet"


COMMANDS = {
    'auth': Authenticate,
    'repos': GetRepos
}


def get_command(command):
    if command in COMMANDS:
        return COMMANDS[command]
    return NotFound
