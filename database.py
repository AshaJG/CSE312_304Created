from pymongo import MongoClient

mongo_client = MongoClient('mongo')
db = mongo_client['ProjectCSE312']
user_collection = db['users']
user_token_collection = db['userTokens']

def store_user(username, password):
    user_collection.insert_one({username: password})
    print(username + ' Store in the database')

def get_user_by_username(username):
    user = user_collection.find({}, {username:1, '_id':0})
    return list(user)

def store_user_token(username, token):
    user = list(user_token_collection.find({}, {username:1, '_id':0}))
    if user:
        user_token_collection.update_one({}, {'$set':{username: token.decode()}})
    else:
        user_token_collection.insert_one({username: token.decode()})

def get_token_by_username(username):
    user = user_token_collection.find({}, {username:1, '_id':0})
    return list(user)