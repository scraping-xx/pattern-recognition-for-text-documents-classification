from pymongo import Connection

db = Connection().theses

c = 0
for f in db.theses.find():
    if 'data' in f and len(f['data']) > 0:
        c += 1

print 'Downloaded ', c

