import json
import sys

from pymongo import MongoClient

mongo_client = MongoClient("mongo")
db = mongo_client["cse312"]  # connecting to db
users_posting_collection = db["posts"]
users_collection = db["users"]
users_id_collection = db["users_id"]

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


# create record
def create(user_dict):
    users_collection.insert_one(user_dict)
    user_dict.pop("_id")
    return user_dict


# create posts to the database
def create_post(p_dict):
    post = users_posting_collection.insert_one(p_dict)
    print("frm db created post", p_dict, flush=True)
    return p_dict

def list_every_post():
    all_posts = users_posting_collection.find({}, {"_id": 0})
    return list(all_posts)
