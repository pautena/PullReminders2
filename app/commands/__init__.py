import urllib.parse
from .implementation import get_command

def parse_command_body(body):

    attr_dict = {
        'args':[],
        'command':None
    }

    if body:
        for attr in body.split("&"):
            key,value = attr.split("=")
            attr_dict[key]=urllib.parse.unquote(value)

            if key == 'text' and value != '':
                attr_dict['args']= value.split('+')
    
    if attr_dict['args']:
        attr_dict['command'] = attr_dict['args'].pop(0)
                
    return attr_dict


def run_command(command):
    print(f"command: {command}")
    return get_command(command['command'])(command)()
