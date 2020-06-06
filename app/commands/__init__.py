
from .implementation import get_command


def run_command(command):
    print(f"command: {command}")
    return get_command(command['command'])(command)()
