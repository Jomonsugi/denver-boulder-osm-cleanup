from pymongo import MongoClient
from pprint import pprint


client = MongoClient()
client = MongoClient('localhost', 27017)
db = client.denver_boulder

#cursor = db.mshanks.find()

#for document in cursor:
    #print(document)
'''
number_documents = db.mshanks.find().count()
print "Number of Documents", number_documents

users = len(db.mshanks.distinct( "created.user" ) )
print "Distinct Users:", users

node_count = db.mshanks.find( {"type":"node"} ).count()
print "Node count:", node_count

way_count = db.mshanks.find( {"type":"way"} ).count()
print "Way count:", way_count

relation_count = db.mshanks.find( {"type":"relation"} ).count()
print "Relation count:", relation_count
'''

#finding zip code count by amenity
id_pipeline =         [
        {"$match" : {"amenity" : "restaurant"}},
        {"$group" : {"_id" : "$address.postcode",
                     "count" : {"$sum" : 1}}
        },
        {"$sort" : {"count" : -1}},
        {"$limit" : 10}
    ]

   
def aggregate(db, id_pipeline):
    result = db.mshanks.aggregate(id_pipeline)
    return result

result = aggregate(db, id_pipeline)

print "Zip code with most entries with amenity: restaurant:"
pprint(list(result))

#finding the top users                 
top_user_pipeline = [        
        {"$group" : {"_id" : "$created.user",
                     "count" : {"$sum" : 1}}
        },
        {"$sort" : {"count" : -1}},
        {"$limit" : 10}
        ]
                   
def aggregate(db, top_user_pipeline):
    result = db.mshanks.aggregate(top_user_pipeline)
    return result

result = aggregate(db, top_user_pipeline)

print "Top User List:"
pprint(list(result))

#number of users appearing only once
one_post_pipeline = [{"$group":{"_id":"$created.user", "count":{"$sum":1}}}, 
                   {"$group":{"_id":"$count", "num_users":{"$sum":1}}}, 
                   {"$sort":{"_id":1}}, {"$limit":1}]
                   
def aggregate(db, one_post_pipeline):
    result = db.mshanks.aggregate(one_post_pipeline)
    return result

result = aggregate(db, one_post_pipeline)

print "Number of Users with only one post:"
pprint(list(result))


