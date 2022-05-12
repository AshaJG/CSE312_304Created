import json
import sys

from pymongo import MongoClient

mongo_client = MongoClient("mongo")
db = mongo_client['ProjectCSE312']

# Create database accordingly
users_posting_collection = db["posts"]  # MAY NEED TO EDIT ACCORDINGLY
users_id_collection = db["users_id"]
user_collection = db['users']
user_token_collection = db['userTokens']
image_id_collection = db["image_id"]
feed_collection = db["feed"]
feed_id_collection = db["feed_id"]
user_profile_collection = db["profile"]


def get_next_id():
    id_object = users_id_collection.find_one({})
    if id_object:
        next_id = int(id_object['last_id']) + 1
        users_id_collection.update_one({}, {'$set': {'last_id': next_id}})
        return next_id
    else:
        users_id_collection.insert_one({'last_id': 1})
        return 1

def get_next_post_id():
    id_object = feed_id_collection.find_one({})
    if id_object:
        next_id = int(id_object['last_id']) + 1
        feed_id_collection.update_one({}, {'$set': {'last_id': next_id}})
        return next_id
    else:
        feed_id_collection.insert_one({'last_id': 1})
        return 1


def get_next_image_id():
    id_object = image_id_collection.find_one({})
    if id_object:
        next_id = int(id_object['last_id']) + 1
        image_id_collection.update_one({}, {'$set': {'last_id': next_id}})
        return next_id
    else:
        image_id_collection.insert_one({'last_id': 1})
        return 1

def store_feed_content(username,image, comment, post_id):
    feed_collection.insert_one({'post_username': username,'post_content': comment.decode(), "post_image": image, "post_id": post_id})

def get_all_feed():
    feed_list = feed_collection.find({},{"_id":0})
    return list(feed_list)


def store_user(username, password):
    user_collection.insert_one({"username": username, "password": password})
    print(username + ' Store in the database')


def get_user_by_username(username):
    user = user_collection.find_one({"username": username}, {"_id": 0})
    return user

def store_user_token(username, token):
    record_exists = user_token_collection.find_one({'username': username})
    if record_exists:
        record = user_token_collection.update_one({'username':username}, {'$set': {'auth_token': token}})
        return record
    else:
        record = user_token_collection.insert_one({'username': username, 'auth_token': token})
        return record


def get_token_by_username(username):
    user = user_token_collection.find_one({'username': username})
    return user


def find_userByToken(token_sent):
    record = user_token_collection.find_one({'auth_token': token_sent})
    return record


def create_profileEdit(profile_dict):
    record = user_profile_collection.insert_one(profile_dict)
    return record


def update_profileEdit(update_dict):
    username = update_dict.get('profile_username')
    p_user = update_dict.get('profile_name')
    p_pic = update_dict.get('profile_pic')
    p_random = update_dict.get('random_info')
    user_profile_collection.update_one({'profile_username': username}, {
        '$set': {'profile_name': p_user, 'profile_pic': p_pic, 'random_info': p_random}})

def find_profileInfo(username):
    record = user_profile_collection.find_one({'profile_username': username})
    return record


def list_profile():
    all_profiles = user_profile_collection.find({}, {'_id': 0})
    return list(all_profiles)


def list_token():
    all_tokens = user_token_collection.find({}, {'_id': 0})
    return list(all_tokens)
