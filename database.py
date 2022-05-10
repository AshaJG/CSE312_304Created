import json
import sys

from pymongo import MongoClient

mongo_client = MongoClient("mongo")
db = mongo_client['ProjectCSE312']

users_id_collection = db["users_id"]
user_collection = db['users']
user_token_collection = db['userTokens']
user_profile_collection = db["profile"]

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
    user_collection.insert_one({"username": username, "password": password})
    print(username + ' Store in the database')


def get_user_by_username(username):
    user = user_collection.find_one({"username": username}, {"_id": 0})
    print("user: ", user)
    return user


# def store_user_token(username, token):
#     user = list(user_token_collection.find({}, {username: 1, '_id': 0}))
#     if user:
#         tempt = user_token_collection.update_one({}, {'$set': {username: token.decode()}})
#         # userToken = user_token_collection.update_one({"username": username},{'$set': {"username": username, "token": token.decode()}})
#         print("user token", tempt, flush = True)
#         return tempt
#     else:
#         tempt = user_token_collection.insert_one({username: token.decode()})
#         # userToken = user_token_collection.insert_one({"username": username, "token": token.decode()})
#         print("user token", tempt, flush=True)
#         return tempt
def store_user_token(username, token):
    record_exists = user_token_collection.find_one({'auth_token': token}, {'$exist': True})
    if record_exists:
        record = user_token_collection.update_one({'auth_token': token},
                                                  {'$set': {'username': username, 'auth_token': token}})
        print('DB the record update:', record, flush=True)
        return record
    else:
        record = user_token_collection.insert_one({'username': username, 'auth_token': token})
        print('DB the record insert:', record, flush=True)
        return record


# def get_token_by_username(username):
#     user = user_token_collection.find({}, {username: 1, '_id': 0})
#     return list(user)


def get_token_by_username(username):
    user = user_token_collection.find_one({'username': username})
    return user


def find_userByToken(token_sent):
    record = user_token_collection.find_one({'auth_token': token_sent})
    return record


def create_profileEdit(profile_dict):
    record = user_profile_collection.insert_one(profile_dict)
    print("record created :", record, flush=True)
    return record


def update_profileEdit(update_dict):
    token = update_dict.get('auth_token')
    p_user = update_dict.get('profile_username')
    p_pic = update_dict.get('profile_pic')
    p_random = update_dict.get('random_info')
    user_profile_collection.update_one({'auth_token': token}, {
        '$set': {'profile_username': p_user, 'profile_pic': p_pic, 'random_info': p_random}})


def find_profileInfo(token_sent):
    record = user_profile_collection.find_one({'auth_token': token_sent})
    return record

def list_profile():
    all_profiles = user_profile_collection.find({},{'_id':0})
    return list(all_profiles)

def list_token():
    all_tokens = user_token_collection.find({},{'_id':0})
    return list(all_tokens)
