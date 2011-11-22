from pymongo import Connection

db = Connection().theses

c = 0
size = 0
avg = 0
invalids = 0
for f in db.theses.find():
    if 'data' in f and len(f['data']) > 0:
        c += 1
        size += len(f['data'])
        if avg == 0:
            avg = len(f['data'])
        elif len(f['data']) < 0.2 * avg:
            print 'Invalid thesis: %s (%d/%d)' % (f['author'], len(f['data']), avg)
            invalids += 1
        else:
            # Moving average
            avg = (avg + len(f['data']))/2.0

print 'Downloaded:', c
print 'Invalid:', invalids

