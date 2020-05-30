import pymongo
import string
import random
import settings


"""
GLOBAL
"""

OAUTH_COLLECTION="oauth"
USERS_COLLECTION="users"
REVIEW_REQUESTS_COLLECTION="reviewRequests"


def _get_db_client():
    return pymongo.MongoClient(settings.DATABASE_URL)[settings.DATABASE]


"""
OAUTH
"""
def _get_oauth_collection():
    return _get_db_client()[OAUTH_COLLECTION]
def _get_users_collection():
    return _get_db_client()[USERS_COLLECTION]

def _generate_state(stringLength=20):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

def get_oauth_instance(user_id,user_name,token,response_url,team_domain):
    collection = _get_oauth_collection() 
    state = _generate_state()
    collection.insert_one({
        '_id':state,        
        'state':state,
        'slack': {
            'user_id':user_id,
            'user_name':user_name,
            'token':token,
            'response_url':response_url,
            'team_domain':team_domain,
        }
    })
    return state

def get_oauth_by_state(state):
    return _get_oauth_collection().find_one({'state' : state})



def login_profile(oauth,profile,access_token):
    collection = _get_users_collection()

    item_id = profile["id"]
    item = {
        "_id":item_id,
        "slack":{
            "user_id":oauth['slack']["user_id"],
            "user_name":oauth['slack']["user_name"],
            "response_url":oauth['slack']["response_url"],
            "team_domain":oauth['slack']["team_domain"]
        },
        "github":{
            "id":profile["id"],
            "user_name":profile["login"],
            "name":profile["name"],
            "access_token":access_token['access_token'],
            "refresh_token":access_token['refresh_token']
        }
    }
    result = collection.replace_one({'_id': item_id}, item, upsert=True)
    print(
        f'update collection -> result: {result}')
    
    return item

def get_profile_by_id(id):
    collection = _get_users_collection()
    return collection.find_one({"_id":id})


"""
REVIEW REQUESTS
"""
def _get_review_requests_collection():
    return _get_db_client()[REVIEW_REQUESTS_COLLECTION]


def _get_review_request_message_id(user_id,pull_request_id):
    return f'{user_id}-{pull_request_id}'

def save_review_request_message(message,ts,channel,user_id,pull_request_id):
    collection = _get_review_requests_collection()
    item_id = _get_review_request_message_id(user_id,pull_request_id)
    item = {
        '_id':item_id,
        'ts':ts,
        'channel':channel,
        'message':message,
        'user':user_id,
        'pull_request':pull_request_id
    }
    result = collection.replace_one({'_id': item_id}, item, upsert=True)
    print("save_review_request_message -> result: ",result)

def get_review_request_message(user_id,pull_request_id):
    item_id = _get_review_request_message_id(user_id,pull_request_id)
    return _get_review_requests_collection().find_one({'_id' : item_id})