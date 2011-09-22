from pymongo import Connection

db = Connection().theses

account = {}
for t in db.theses.find():
    if 'data' in t and len(t['data']) > 10:
        if t['field'] not in account:
            account[t['field']] = 0

        account[t['field']] += 1

print 'total:',account

