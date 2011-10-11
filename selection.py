# -*- coding: utf-8 -*-
import operator
import numpy

from pymongo import Connection

from bag import bag_of_words

db = Connection().theses
db.features.ensure_index('field')

def has_data(doc):
    return 'data' in doc and len(doc['data']) > 0

def df():
    """ Document frequency thresholding (DF) """
    account = {}
    freqs = {}

    for t in db.theses.find():
        if 'data' in t and len(t['data']) > 10:
            if t['field'] not in account:
                account[t['field']] = 0
            account[t['field']] += 1
    print 'total:', account

    for field in account:
        print 'Creating frequency map for', field
        f = {}
        for t in db.theses.find({'field': field}):
            if 'data' not in t or len(t['data']) == 0:
                continue
            bag = bag_of_words(t['data'])
            for item in bag:
                if item not in f:
                    f[item] = 1
                else:
                    f[item] += 1
        freqs[field] = f

    print 'Found frequencies, now filtering...'

    for name, field in freqs.items():
        fcut = (0.3*numpy.max(field.values()) + 0.7*numpy.mean(field.values()))/2.0
        freqs[name] = dict((k, v) for k, v in field.iteritems() if v > fcut)

        max = numpy.max(freqs[name].values())
        min = numpy.min(freqs[name].values())
        print '\n%s (cut=%d, min=%d, max=%d)' % (name, fcut, min, max)
        print '\tfeature dimension=%d' % len(freqs[name])
        print '\tMost frequent:', freqs[name].keys()[0:10]

        db.features.update({"field": name}, {"field": name, "features": freqs[name]}, upsert=True)

def mi():
    """ Mutual Information for term t and category c

    A - ndocs where t and c co-occur
    B - ndocs where t and not c occurs
    C - ndocs where c and not t occurs
    N - total of docs
    """

    def I(A, B, C, N):
       return numpy.log(A * N / float((A + C) * (A + B)))

    # Find one with data
    doc = db.theses.find_one({'data': { '$exists': True }})
    bag = bag_of_words(doc['data'])
    field = doc['field']

    print 'Computing MI for category', field
    # Compute I(t, c) for each bag term
    for term in bag:
        A = 0
        B = 0
        C = 0
        N = 0

        for doc in db.theses.find():
            if not has_data(doc):
                continue

            _bag = bag_of_words(doc['data'])

            if doc['field'] == field and term in _bag:
                A += 1
            elif doc['field'] != field and term in _bag:
                B += 1
            elif doc['field'] == field and term not in _bag:
                C += 1

            N += 1
        print 'Term: %s (A=%d, B=%d, C=%d, N=%d), MI=%.4f' % (term, A, B, C, N, I(A, B, C, N))

def chi_sqr():
    """ chi-square statistic (CHI)
    A - ndocs where t and c co-occur
    B - ndocs where t and not c occurs
    C - ndocs where c and not t occurs
    D - ndocs where neither c or t occurs
    N - total of docs
    """

    def chisqr(A, B, C, D, N):
        den = (A + C) * (B + D) * (A + B) * (C + D)
        if den == 0:
            return -10**5
        return (N * (A * D - C * B)**2) / den

    # Find one with data
    doc = db.theses.find_one({'data': { '$exists': True }})
    bag = bag_of_words(doc['data'])
    field = doc['field']

    print 'Computing chi^2 for category', field
    # Compute I(t, c) for each bag term
    for term in bag:
        A = 0
        B = 0
        C = 0
        D = 0
        N = 0

        for doc in db.theses.find():
            if not has_data(doc):
                continue

            _bag = bag_of_words(doc['data'])

            if doc['field'] == field and term in _bag:
                A += 1
            elif doc['field'] != field and term in _bag:
                B += 1
            elif doc['field'] == field and term not in _bag:
                C += 1
            else:
                D += 1

            N += 1
        print 'Term: %s (A=%d, B=%d, C=%d, D=%d, N=%d), chi^2=%.4f' % (term, A, B, C, D, N, chisqr(A, B, C, D, N))


if __name__ == '__main__':
    df()
    mi()
    chi_sqr()
