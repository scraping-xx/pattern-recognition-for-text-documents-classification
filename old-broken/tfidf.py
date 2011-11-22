import numpy

from pymongo import Connection

from bag import *


# tf, idf implementation for frequency bag-of-words representation

def idf(term, docs):
    D = 0 #docs.count()
    d = 0
    for doc in docs:
        if 'data' not in doc or len(doc['data']) == 0:
            continue
        if term in bag_of_words(doc['data']):
            d += 1
        D += 1

    return numpy.log(D/(1.0+d))

def tf(term, doc):
    return doc[term]

def tf_idf(term, doc, docs):
    return idf(term, docs) * tf(term, doc)


if __name__ == '__main__':
    db = Connection().theses
    field = 'Engenharia de Sistemas'
    #features = db.features.find_one({'field': field}, {'features': 1})['features']
    for doc in db.theses.find({'field': field}):
        if 'data' not in doc or len(doc['data']) == 0:
            continue

        bag = frequency_bag(doc['data'])

        print 'Calculating tf-idf for thesis', doc['author']
        for term in bag:
            print '%s\t%.4f' % (term, tf_idf(term, bag, db.theses.find({'field': field})))
