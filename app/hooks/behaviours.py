from slack import update_message


class PullRequestable:
    action = {}

    def get_pull_request(self):
        pull_request = self.action["pull_request"]
        return {
            'id': pull_request['id'],
            'url': pull_request['html_url'],
            'repo': pull_request["base"]["repo"]["name"],
            'number': pull_request["number"],
            'title': pull_request["title"]
        }


class Strikethroughable:
    @staticmethod
    def strikethrough_review_request(message):
        print('message["message"]: ', message["message"])
        update_message(
            f'~{message["message"]}~',
            message['ts'],
            message['channel']
        )
