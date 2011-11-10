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
    stats = dict.fromkeys(classes)
    for k in stats:
        stats[k] = {'success': 0, 'errors': 0}

    for doc in test_docs.find():
        if not data_valid(doc): continue
        c = nb_classify(classes, vocabulary, prior, cond, doc)
        if c == doc['field']:
            print 'Success (%s/%s)' % (doc['author'], doc['field'])
            stats[doc['field']]['success'] += 1
        else:
            print 'Error (%s/%s)' % (doc['author'], doc['field'])
            stats[doc['field']]['errors'] += 1

    print stats

    success = 0.0
    errors = 0.0

    for cls, stat in stats.iteritems():
        print 'Class', cls, '(fp=%d,tp=%d)' % (stat['errors'], stat['success'])
        success += stat['success']
        errors += stat['errors']
        precision = stat['success']/float(sum(stat.values()))
        recall = stat['success']/float(stat['success'] + 0)
        f1 = 2.0 * precision * recall / (precision + recall)

        print '\tPrecision:\t%.3f' % (precision)
        print '\tRecall:\t%.3f' % (recall)
        print '\tF1:\t%.3f' % (f1)
        print

    print 'Global accuracy: %.2f %%' % (success/float(success + errors))
