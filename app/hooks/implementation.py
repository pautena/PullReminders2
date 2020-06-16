
from slack import update_message
from repository import get_profile_by_id, save_review_request_message, \
    get_review_request_message, save_comment, get_comment_by_id, \
    get_review_request_messages_by_pull_request, clean_pull_request_data
from .behaviours import PullRequestable, Strikethroughable, Ownerable
from .base import BaseAction, get_user_display_name


class ReviewRequestedAction(BaseAction, PullRequestable):

    def requested_by(self):
        pr_user = self.action["pull_request"]["user"]
        user_id = pr_user["id"]
        profile = get_profile_by_id(user_id)

        if profile:
            return {
                'user_id': profile["slack"]["user_id"],
                'user_name': profile["slack"]["user_name"]
            }
        return {
            'user_name': pr_user["login"]
        }

    def get_requested_reviewer(self):
        reviewer = self.action["requested_reviewer"]
        return get_profile_by_id(reviewer["id"])

    def __call__(self):
        print("ReviewRequested")
        requested_by = self.requested_by()
        pull_request = self.get_pull_request()
        reviewer = self.get_requested_reviewer()
        print(f"reviewer: ", reviewer)
        if reviewer:
            self.send_review_requested_message(
                reviewer, requested_by, pull_request)

    def send_review_requested_message(
            self, reviewer, requested_by, pull_request):
        user_id = reviewer["github"]["id"]

        # pylint: disable=C0301
        user = f"<@{requested_by['user_id']}>" if 'user_id' in requested_by else requested_by["user_name"]

        # pylint: disable=C0301
        message = f'{user} requested your review on [{pull_request["repo"]}#{pull_request["number"]}] <{pull_request["url"]}|{pull_request["title"]}>'

        review_request_message = get_review_request_message(
            user_id, pull_request['id'])

        if review_request_message is None:
            result = self.send_message(message, reviewer["slack"]["user_id"])
            if result:
                save_review_request_message(
                    message,
                    result["ts"],
                    result["channel"],
                    user_id,
                    pull_request["id"])
        else:
            update_message(
                message,
                review_request_message['ts'],
                review_request_message['channel'])


class ApprovedSubmitReviewAction(
        BaseAction,
        PullRequestable,
        Strikethroughable,
        Ownerable):

    def get_reviewer_user(self):
        return self.action['review']['user']

    def __call__(self):
        print("AprovedSubmitReview")
        self.notify_reviewer_user()
        self.notify_pull_request_owner()

    def notify_reviewer_user(self):
        pull_request = self.get_pull_request()
        user = self.get_reviewer_user()
        review_request_message = get_review_request_message(
            user['id'], pull_request['id'])
        print("review_request_message: ", review_request_message)

        if review_request_message:
            self.strikethrough_review_request(review_request_message)

    def notify_pull_request_owner(self):
        owner = self.get_owner()
        user = self.get_reviewer_user()
        pull_request = self.get_pull_request()
        owner_profile = get_profile_by_id(owner["id"])
        user_profile = get_profile_by_id(user["id"])
        user_name = get_user_display_name(user['login'], user_profile)
        if owner_profile:
            # pylint: disable=C0301
            message = f'{user_name} approved [{pull_request["repo"]}#{pull_request["number"]}] <{pull_request["url"]}|{pull_request["title"]}>'
            self.send_message(message, owner_profile['slack']['user_id'])


class RemoveApprovalSubmitReviewAction(BaseAction, PullRequestable):

    def get_user(self):
        return self.action['review']['user']

    def __call__(self):
        print("RemoveApprovalSubmitReview")
        pull_request = self.get_pull_request()
        user = self.get_user()
        review_request_message = get_review_request_message(
            user['id'], pull_request['id'])

        print("review_request_message: ", review_request_message)

        if review_request_message:
            update_message(
                review_request_message["message"],
                review_request_message['ts'],
                review_request_message['channel']
            )


class ChangesRequestedSubmitReviewAction(RemoveApprovalSubmitReviewAction):
    pass


class CommentedSubmitReviewAction(BaseAction, PullRequestable, Ownerable):
    def __call__(self):
        print("CommentedSubmitReviewAction")
        self._notify_pull_request_owner()

    def get_reviewer_user(self):
        return self.action['review']['user']

    def _notify_pull_request_owner(self):

        if not self.action['review']['body']:
            return

        owner = self.get_owner()
        user = self.get_reviewer_user()

        if owner['id'] == user['id']:
            return

        pull_request = self.get_pull_request()
        owner_profile = get_profile_by_id(owner["id"])
        user_profile = get_profile_by_id(user["id"])
        user_name = get_user_display_name(user['login'], user_profile)
        if owner_profile:
            # pylint: disable=C0301
            message = f'{user_name} commented on [{pull_request["repo"]}#{pull_request["number"]}] <{self.action["review"]["html_url"]}|{pull_request["title"]}>'

            attachments = [{
                "color": "#355C7D",
                "text": f"{user_name}: {self.action['review']['body']}",
            }]
            self.send_message(
                message,
                owner_profile['slack']['user_id'],
                attachments=attachments)


class SubmitReviewAction(BaseAction):
    REVIEW_TYPE = {
        'approved': ApprovedSubmitReviewAction,
        'changes_requested': ChangesRequestedSubmitReviewAction,
        'commented': CommentedSubmitReviewAction
    }

    def get_type(self):
        return self.action['review']['state']

    def __call__(self):
        review_type = self.get_type()
        print("SubmitReview. review_type: ", review_type)
        if review_type in self.REVIEW_TYPE:
            return self.REVIEW_TYPE[review_type](self.action)()
        return None


class CreatedActionReview(BaseAction):
    def get_pull_request(self):
        if 'pull_request' in self.action:
            return self.action["pull_request"]
        if 'issue' in self.action:
            return self.action["issue"]
        return None

    def _process_comment(self):
        comment = self.action["comment"]

        save_comment(
            comment["id"],
            comment["user"]["id"],
            self.get_pull_request()["id"],
        )

    def _process_repply(self):

        if 'in_reply_to_id' not in self.action["comment"]:
            return

        pull_request = self.action["pull_request"]
        replied_comment = get_comment_by_id(
            pull_request["id"],
            self.action["comment"]['in_reply_to_id']
        )

        if not replied_comment:
            return

        replied_profile = get_profile_by_id(replied_comment['user_id'])
        sender_profile = get_profile_by_id(
            self.action["comment"]["user"]['id'])

        sender_name = get_user_display_name(
            self.action["comment"]["user"]['login'], sender_profile)

        if not replied_profile:
            return

        if sender_profile is not None and replied_profile["slack"][
                "user_name"] == sender_profile["slack"]["user_name"]:
            return

        repository = self.action["repository"]
        attachments = [{
            "color": "#355C7D",
            "text": f"{sender_name}: {self.action['comment']['body']}",
        }]

        # pylint: disable=C0301
        message = f'{sender_name} repplied to you in [{repository["name"]}#{pull_request["number"]}] ' + \
            f'<{self.action["comment"]["html_url"]}|{pull_request["title"]}>'
        self.send_message(
            message,
            replied_profile['slack']['user_id'],
            attachments)


class CreatedActionIssue(BaseAction):
    def get_issue_pull_request(self):
        return self.action['issue']

    def get_issue_owner(self):
        return self.get_issue_pull_request()['user']

    def get_issue_repo(self):
        return self.action['repository']

    def get_issue_comment_user(self):
        return self.action['comment']['user']

    @staticmethod
    def _is_valid_user(user):
        return user['type'] != 'Bot'

    def _process_issue_comment(self):
        owner = self.get_issue_owner()

        user = self.get_issue_comment_user()

        if not self._is_valid_user(user):
            return

        if owner['login'] == user['login']:
            return

        pull_request = self.get_issue_pull_request()
        owner_profile = get_profile_by_id(owner["id"])
        user_profile = get_profile_by_id(user["id"])

        repo = self.get_issue_repo()
        user_name = get_user_display_name(user['login'], user_profile)

        if owner_profile:

            # pylint: disable=C0301
            message = f'{user_name} commented on [{repo["name"]}#{pull_request["number"]}] <{self.action["comment"]["html_url"]}|{pull_request["title"]}>'

            attachments = [{
                "color": "#355C7D",
                "text": f"{user_name}: {self.action['comment']['body']}",
            }]
            self.send_message(
                message,
                owner_profile['slack']['user_id'],
                attachments=attachments)


class CreatedAction(CreatedActionReview, CreatedActionIssue):
    def __call__(self):
        print("CreatedAction")

        if 'comment' in self.action and 'pull_request' in self.action:
            self._process_comment()
            self._process_repply()
        elif 'comment' in self.action and 'issue' in self.action:
            self._process_issue_comment()


class ClosedAction(BaseAction, PullRequestable, Strikethroughable):

    def __call__(self):
        print("ClosedAction")

        review_requests = self.get_pull_request_review_requests()

        for review_request in review_requests:
            self.notify_close(review_request)
        
        clean_pull_request_data(self.get_pull_request()['id'])

    def get_pull_request_review_requests(self):
        return get_review_request_messages_by_pull_request(
            self.get_pull_request()["id"])

    def notify_close(self, review_request):
        profile = get_profile_by_id(review_request['user'])
        print("review_request: ", review_request, ", profile: ", profile)

        if profile:
            self.strikethrough_review_request(review_request)
