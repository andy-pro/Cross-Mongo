# -*- coding: utf-8 -*-

import pymongo
#from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime

#client = pymongo.MongoClient('mongodb://localhost:8001/')
client = pymongo.MongoClient('localhost', 8001)
db = client.test_database


plints = db.plints
plint = {
    "title": "M3",
    "modon": datetime.datetime.utcnow(),
    "modby": "Rurak",
    "comdata": "LAZ 0V M10",
    "start1": True,
    "pairs": [
      { "title": "Cranty",
        "modon": datetime.datetime.utcnow(),
        "modby": "Pobran",
        "details": "za polosoy",
        "parallel": False,
        "color": 5,
        "pos": 1 },
      { "title": "Test pair",
        "modon": datetime.datetime.utcnow(),
        "modby": "Rurak",
        "details": "Cool pair",
        "parallel": False,
        "color": 2,
        "pos": 3 },
      { "title": "Popandes",
        "modon": datetime.datetime.utcnow(),
        "modby": "Savitsky",
        "details": "dvor-dme",
        "parallel": True,
        "color": 7,
        "pos": 6 },
      { "title": "Python",
        "modon": datetime.datetime.utcnow(),
        "modby": "Andy-Pro",
        "details": "forever",
        "parallel": False,
        "color": 0,
        "pos": 8 }
    ]
    }
#plint_id = plints.insert_one(plint).inserted_id

#post_id = '5700bb4e13e0ec14e432ca2a'
plint_id = '5700d29813e0ec12c431ce1a'
#print plint_id

#print db.collection_names(include_system_collections=False)

#plint_id = ObjectId(plint_id)

#plint = plints.find_one({'_id': plint_id})
q = 'Dvor-dme'
q = {"$regex": 'dvo', "$options":"i"}
#q = {"$regex": '/pop/i'}
#rows = plints.find( { "$or": [ { "pairs[0].title": q } ] } )


#rows = plints.find( { 'pairs':  { '$elemMatch' : { 'title' : q, 'details': q } } } )
rows = plints.find( { '$or' : [ { 'comdata': q }, { 'pairs.title': q }, {'pairs.details': q } ] } )

#rows = plints.find( { 'pairs.title' : 'dvor-dme' }  )
#print plints.find_one( { 'pairs.title' : 'dvor-dme' }  )


for row in rows:
    print row['title'], row['modby']
    #print row['title']

'''
db1 = client.cross
Crosses = db1.crosses
Verticals = db1.verticals
rows = Crosses.find()

for row in rows:
    #print row['title'], row['modby']
    print row['_id'], row['title'], type(row)
    subrows = Verticals.find({'cross':row['_id']})
    for w in subrows:
        print '\t', w['title']


#cr = dict(crosses=[(r['_id'], r['title'], [(w['_id'], w['title']) for w in Verticals.find({'cross':r['_id']})]) for r in Crosses.find()])
#print cr
#return dict(crosses=[(r.id, r.title, [(w.id, w.title) for w in db(db.verticals.cross == r.id).select()]) for r in rows])
'''