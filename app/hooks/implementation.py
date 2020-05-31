
from repository import get_profile_by_id,save_review_request_message,get_review_request_message,save_comment,get_comment_by_id
from slack import send_message,update_message

class BaseAction:
    def __init__(self,action):
        self.action=action
    
    def get_name(self):
        self.get_param('action')
    
    def get_param(self,param):
        return self.action.get(param,None)
    
    def __call__(self):
        pass

    def send_message(self,message,user_id,attachments=[]):
        return send_message(message,user_id,attachments=attachments)

class NotFound(BaseAction):
    def __call__(self):
        print("NotFound")
        return f"Action {self.get_name()} not found"


class PullRequestable:
    def get_pull_request(self):
        pr = self.action["pull_request"]
        return {
            'id':pr['id'],
            'url':pr['html_url'],
            'repo':pr["base"]["repo"]["name"],
            'number':pr["number"],
            'title':pr["title"]

        }

class ReviewRequestedAction(BaseAction,PullRequestable):

    def requested_by(self):
        pr_user = self.action["pull_request"]["user"]
        user_id = pr_user["id"]
        profile = get_profile_by_id(user_id)

        if profile:
            return {
                'user_id':profile["slack"]["user_id"],
                'user_name':profile["slack"]["user_name"]
            }
        else:
            return {
                'user_name':pr_user["login"]
            }

        return profile if profile is not None else self.action["pull_request"]["user"]

    def get_requested_reviewers(self):
        reviewers = []
        for reviewer in self.action["pull_request"]["requested_reviewers"]:
            profile = get_profile_by_id(reviewer["id"])
            if profile:
                reviewers.append(profile)
        return reviewers
    

    def __call__(self):
        print("ReviewRequested")
        requested_by = self.requested_by()
        pull_request = self.get_pull_request()
        for reviewer in self.get_requested_reviewers():
            print(f"reviewer: ",reviewer)
            self.send_review_requested_message(reviewer,requested_by,pull_request)
        
    def send_review_requested_message(self,reviewer,requested_by,pull_request):
        user_id = reviewer["github"]["id"]
        user = f"@{requested_by['user_name']}" if 'user_id' in requested_by else requested_by["user_name"]

        message = f'{user} requested your review on [{pull_request["repo"]}#{pull_request["number"]}] ' + \
            f'<{pull_request["url"]}|{pull_request["title"]}>'


        review_request_message = get_review_request_message(user_id,pull_request['id'])

        if review_request_message is None:
            result = self.send_message(message,reviewer["slack"]["user_id"])
            save_review_request_message(message,result["ts"],result["channel"],user_id,pull_request["id"])
        else:
            update_message(message,review_request_message['ts'],review_request_message['channel'])
        

class ApprovedSubmitReviewAction(BaseAction,PullRequestable):

    def get_user(self):
        return self.action['review']['user']

    def __call__(self):
        print("AprovedSubmitReview")
        pull_request= self.get_pull_request()
        user = self.get_user()
        review_request_message = get_review_request_message(user['id'],pull_request['id'])
        print("review_request_message: ",review_request_message)

        update_message(
            f'~{review_request_message["message"]}~',
            review_request_message['ts'],
            review_request_message['channel']
        )

class RemoveApprovalSubmitReviewAction(BaseAction,PullRequestable):

    def get_user(self):
        return self.action['review']['user']

    def __call__(self):
        print("RemoveApprovalSubmitReview")
        pull_request= self.get_pull_request()
        user = self.get_user()
        review_request_message = get_review_request_message(user['id'],pull_request['id'])

        print("review_request_message: ",review_request_message)

        if review_request_message:
            update_message(
                review_request_message["message"],
                review_request_message['ts'],
                review_request_message['channel']
            )


class ChangesRequestedSubmitReviewAction(RemoveApprovalSubmitReviewAction):
    pass

class CommentedSubmitReviewAction(BaseAction):
    pass

class SubmitReviewAction(BaseAction):
    REVIEW_TYPE = {
        'approved':ApprovedSubmitReviewAction,
        'changes_requested':ChangesRequestedSubmitReviewAction,
        'commented':CommentedSubmitReviewAction
    }

    def get_type(self):
        return self.action['review']['state']

    def __call__(self):
        review_type = self.get_type()
        print("SubmitReview. review_type: ",review_type)
        if review_type in self.REVIEW_TYPE:
            return self.REVIEW_TYPE[review_type](self.action)()
        return None


class CreatedAction(BaseAction):
    def __call__(self):
        print("CreatedAction")

        if 'comment' in self.action:
            self._process_comment()
            self._process_repply()
        
    
    def _process_comment(self):
        comment = self.action["comment"]

        save_comment(
            comment["id"],
            comment["body"],
            comment["user"]["id"],
            comment["user"]["login"],
            self.action["pull_request"]["id"],
        )

        #TODO: If not repply, send message to pr creator
    
    def _process_repply(self):

        if not 'in_reply_to_id' in self.action["comment"]:
            return
            
        pull_request  = self.action["pull_request"]
        replied_comment = get_comment_by_id(
            pull_request["id"],
            self.action["comment"]['in_reply_to_id']
        )

        if not replied_comment:
            return

        replied_profile = get_profile_by_id(replied_comment['user_id'])
        sender_profile = get_profile_by_id(self.action["comment"]["user"]['id'])


        replied_name = f'@{replied_profile["slack"]["user_name"]}'
        sender_name = self.action["comment"]["user"]['login']
        if sender_profile:
            sender_name = f'@{sender_profile["slack"]["user_name"]}'

        if not replied_profile:
            return
        
        if sender_profile is not None and replied_profile["slack"]["user_name"] == sender_profile["slack"]["user_name"]:
            return

        repository = self.action["repository"]
        attachments = [{
            "color": "#FF0000",
            "text": f"{replied_name}: {replied_comment['body']}",
        },{
            "color": "#00FF00",
            "text": f"{sender_name}: {self.action['comment']['body']}",
        }]

        message = f'{sender_name} repplied to you in [{repository["name"]}#{pull_request["number"]}] ' + \
            f'<{pull_request["url"]}|{pull_request["title"]}>'
        self.send_message(message,replied_profile['slack']['user_id'],attachments)


ACTIONS = {
    'review_requested':ReviewRequestedAction,
    'submitted':SubmitReviewAction,
    'created':CreatedAction
}

def get_action(action):
    if action in ACTIONS:
        return ACTIONS[action]
    return NotFound

