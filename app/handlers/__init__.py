import urllib.parse


def parse_command_body(body):

    attr_dict = {
        'args': [],
        'command': None
    }

    if body:
        for attr in body.split("&"):
            key, value = attr.split("=")
            attr_dict[key] = urllib.parse.unquote(value)

            if key == 'text' and value != '':
                attr_dict['args'] = value.split('+')

    if attr_dict['args']:
        attr_dict['command'] = attr_dict['args'].pop(0)

    return attr_dict
