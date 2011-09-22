import operator
import numpy
from pymongo import Connection

db = Connection().theses
account = {}
for t in db.theses.find():
    if 'data' in t and len(t['data']) > 10:
        if t['field'] not in account:
            account[t['field']] = 0
        account[t['field']] += 1
print 'total:',account


def get_bag_of_words(data):
    # Cleanup numbers
    for i in range(10):
        data = data.replace('%d' % i, '')

    # Cleanup separation chars
    data = data.replace(',', ' ')
    data = data.replace('/', ' ')
    data = data.replace('(', ' ')
    data = data.replace(')', ' ')
    data = data.replace('.', ' ')

    # Lower
    data = data.lower()

    # Split everything
    data = data.split()

    # Convert to set
    return set(data)


freqs = {}
for field in account:
    print 'Creating frequency map for', field
    f = {}
    for t in db.theses.find({'field': field}):
        # Wrong data
        if 'data' not in t:
            continue

        bag = get_bag_of_words(t['data'])
        for item in bag:
            if item not in f:
                f[item] = 1
            else:
                f[item] += 1
    freqs[field] = f

print 'Found frequencies, now filtering...'

for name, field in freqs.items():
    fcut = (numpy.max(field.values()) + numpy.mean(field.values()))/2.0
    print '\tCut frequency for %s is %.2f' % (name, fcut)
    freqs[name] = dict((k, v) for k, v in field.iteritems() if v > fcut)
    print '\tLength: %d' % len(freqs[name])
    print '\tMost frequent:', freqs[name].keys()[0:10]
    print '\tMinimum frequency:', numpy.min(freqs[name].values())
