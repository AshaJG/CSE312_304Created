import json
import sys

from pymongo import MongoClient

mongo_client = MongoClient("mongo")
db = mongo_client["cse312"]  # connecting to db
users_posting_collection = db["posts"]  # MAY NEED TO EDIT ACCORDINGLY
users_id_collection = db["users_id"]

mongo_client = MongoClient('mongo')
db = mongo_client['ProjectCSE312']
user_collection = db['users']
user_token_collection = db['userTokens']

print("starting db..")


def get_next_id():
    id_object = users_id_collection.find_one({})
    if id_object:
        next_id = int(id_object['last_id']) + 1
        users_id_collection.update_one({}, {'$set': {'last_id': next_id}})
        return next_id
    else:
        users_id_collection.insert_one({'last_id': 1})
        return 1


def store_user(username, password):
    user_collection.insert_one({username: password})
    print(username + ' Store in the database')


def get_user_by_username(username):
    user = user_collection.find({}, {username: 1, '_id': 0})
    return list(user)


def store_user_token(username, token):
    tempt = {}
    user = list(user_token_collection.find({}, {username: 1, '_id': 0}))
    if user:
        tempt = user_token_collection.update_one({}, {'$set': {username: token.decode()}})
    else:
        tempt = user_token_collection.insert_one({username: token.decode()})


def get_token_by_username(username):
    user = user_token_collection.find({}, {username: 1, '_id': 0})
    return list(user)


# create posts to the database
def create_post(p_dict):
    post = users_posting_collection.insert_one(p_dict)
    print("frm db created post", p_dict, flush=True)
    return p_dict


def list_every_post():
    all_posts = users_posting_collection.find({}, {"_id": 0})
    return list(all_posts)
