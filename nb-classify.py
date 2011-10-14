import numpy
import operator

from training_result import vocabulary, prior, cond
from pymongo import Connection

from bag import tokenize

db = Connection().theses

def data_valid(doc):
    return True if 'data' in doc and len(doc['data']) > 0 else False

def nb_classify(classes, vocabulary, prior, cond, doc):
    tokens = tokenize(doc['data'])
    score = {}
    for cls in classes:
        score[cls] = numpy.log(prior[cls])

        for term in tokens:
            if term in cond:
                score[cls] += numpy.log(cond[term][cls])
    return max(score.iteritems(), key=operator.itemgetter(1))[0]

if __name__ == '__main__':
    test_docs = db.testing
    classes = list(set([d['field'] for d in db.theses.find({}, {'field': 1})]))
    stats = {'success': 0, 'errors': 0}

    for doc in test_docs.find():
        if not data_valid(doc): continue
        c = nb_classify(classes, vocabulary, prior, cond, doc)
        if c == doc['field']:
            print 'Success (%s)' % doc['author']
            stats['success'] += 1
        else:
            print 'Error (%s)' % doc['author']
            stats['errors'] += 1
    print 'Stats:', stats
