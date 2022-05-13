from email import message_from_string
from genericpath import exists
import json
import re
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
like_collection = db['like_postId']
user_profile_collection = db["profile"]
user_dm_collection = db["dms"]

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


def store_feed_content(username,image, comment, post_id, profile_pic):
    feed_collection.insert_one({'post_username': username,'post_content': comment.decode(), "post_image": image, "post_id": post_id, 'post_user_image':profile_pic})


def get_all_feed():
    feed_list = feed_collection.find({}, {"_id": 0})
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
        record = user_token_collection.update_one({'username': username}, {'$set': {'auth_token': token}})
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


def create_likeId(like_dict):
    record = like_collection.insert_one(like_dict)
    return record


def find_post(post_id):
    record = like_collection.find_one({'post_ID': post_id}, {"_id": 0})
    print("in find post db", post_id)
    return record


def update_postCount(post_id, count):
    record = like_collection.update_one({'post_ID': post_id}, {'$set': {'like': count}})


def list_profile():
    all_profiles = user_profile_collection.find({}, {'_id': 0})
    return list(all_profiles)


def list_token():
    all_tokens = user_token_collection.find({}, {'_id': 0})
    return list(all_tokens)

def add_dm(sender, reciever):
    dm_exists1 = user_dm_collection.find_one({'user1': sender}, {'$exist':True})
    dm_exists2 = user_dm_collection.find_one({'user2': sender}, {'$exist':True})
    dm_exists3 = user_dm_collection.find_one({'user1': reciever}, {'$exist':True})
    dm_exists4 = user_dm_collection.find_one({'user2': reciever}, {'$exist':True})
    if(dm_exists1 and dm_exists4):
        return "already exsists"
    elif(dm_exists2 and dm_exists3):
        return "already exsists"
    else:
        datadict = {'user1': sender, 'user2': reciever, 'dms': []}
        record = user_dm_collection.insert_one(datadict)
        return record

def get_dm(sender, reciever):    
    dm_exists1 = user_dm_collection.find_one({'user1': sender}, {'$exist':True})
    dm_exists2 = user_dm_collection.find_one({'user2': sender}, {'$exist':True})
    dm_exists3 = user_dm_collection.find_one({'user1': reciever}, {'$exist':True})
    dm_exists4 = user_dm_collection.find_one({'user2': reciever}, {'$exist':True})
    if(dm_exists1 and dm_exists4):
        data = user_dm_collection.find_one({'user1': sender, 'user2': reciever})
        return data['dms']
    elif(dm_exists2 and dm_exists3):
        data = user_dm_collection.find_one({'user1': reciever, 'user2': sender})
        return data['dms']
    else:
        return "does not exsist"

def add_dm_message(sender, reciever, message):
    dm_exists1 = user_dm_collection.find_one({'user1': sender}, {'$exist':True})
    dm_exists2 = user_dm_collection.find_one({'user2': sender}, {'$exist':True})
    dm_exists3 = user_dm_collection.find_one({'user1': reciever}, {'$exist':True})
    dm_exists4 = user_dm_collection.find_one({'user2': reciever}, {'$exist':True})
    if(dm_exists1 and dm_exists4):
        print("updating dms")
        sys.stdout.flush()
        data = user_dm_collection.find_one({'user1': sender,'user2': reciever})
        update = data['dms']
        print(update)
        sys.stdout.flush()
        update.append(message)
        print(update)
        sys.stdout.flush()
        record = user_dm_collection.update_one({'user1': sender, 'user2': reciever}, {'$set': {'dms': update}})
        return record
    elif(dm_exists2 and dm_exists3):
        print("updating dms")
        sys.stdout.flush()
        data = user_dm_collection.find_one({'user1': reciever,'user2': sender})
        update = data['dms']
        print(update)
        sys.stdout.flush()
        update.append(message)
        print(update)
        sys.stdout.flush()
        record = user_dm_collection.update_one({'user1': reciever, 'user2': sender}, {'$set': {'dms': update}})
        return record

def find_all_dms(user):
    print("FINDING ALL DMS")
    dm1 = list(user_dm_collection.find({'user1': user}, {'_id':0, 'dms': 0, 'user1': 0}))
    dm2 = list(user_dm_collection.find({'user2': user}, {'_id':0, 'dms':0, 'user2': 0}))
    print(dm1)
    sys.stdout.flush()
    print(dm2)
    sys.stdout.flush()
    dms =[]
    for entry in dm1:
        dms.append({'user':entry["user2"]})
    for entry in dm2:
        dms.append({'user':entry["user1"]})
    print(dms)
    sys.stdout.flush
    if(dms == []):
        return "none"
    else:
        return dms