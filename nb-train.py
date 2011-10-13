# -*- coding: utf-8 -*-

import numpy
import tempfile
import subprocess

import sys
import os
import os.path

from pymongo import Connection

db = Connection().theses

from bag import tokenize, bag_of_words


def data_valid(doc):
    return True if 'data' in doc and len(doc['data']) > 0 else False

def extract_vocabulary(docs):
    f = {}
    for doc in docs.find():
        if not data_valid(doc): continue

        for term in bag_of_words(doc['data']):
            if term not in f:
                f[term] = 1
            else:
                f[term] += 1

    # TODO change this
    mean = (numpy.max(f.values()) + numpy.mean(f.values()))/2.0
    return dict(filter(lambda n: n[1] >= mean, f.iteritems()))

def train(classes, docs):
    n = docs.count()
    prior = {}
    cond = {}

    print 'Extracting vocabulary...',
    vocabulary = extract_vocabulary(docs)
    print 'done (d=%d words)' % len(vocabulary)

    for cls in classes:
        print 'Computing prior/conditional probs for class %s' % cls
        nc = docs.find({'field': cls}).count()
        prior[cls] = nc/float(n)

        print '  Computing term frequency...'
        nterm = {}

        print '  big text'
        textfile = tempfile.NamedTemporaryFile()
        for doc in docs.find({'field': cls}):
            if not data_valid(doc): continue
            textfile.write((' '.join(tokenize(doc['data'])) + ' ').encode('utf-8', 'replace'))
        textfile.flush()
        print '  counting..'

        for term in vocabulary:
            if term not in nterm:
                nterm[term] = 0

            os.system(("tr -cs 'A-Za-z' '\\n' < %s | grep -c '%s' > count" % (textfile.name, term)).encode('utf-8', 'replace'))
            count = int(open('count', 'r').read())
            print '%d/%d, n=%d' % (vocabulary.keys().index(term), len(vocabulary), count)

            if count > 1000:
                print 'Warning: term %s has over 1k occurences (n=%d)' % (term, count)
            nterm[term] += count
        print 'Done'

        print '  Computing conditional probabilities...',
        for term in vocabulary:
            if term not in cond:
                cond[term] = {}
            if cls not in cond[term]:
                cond[term][cls] = {}
            cond[term][cls] = (nterm[term] + 1)/float(sum([t + 1 for t in nterm.values()]))
        print 'Done'

        print cond

    return vocabulary, prior, cond


if __name__ == '__main__':
    total_docs = db.theses.count()
    training_docs = db.theses.find().limit(int(0.5*total_docs))

    for doc in training_docs:
        db.training.save(doc, safe=True)

    for doc in db.theses.find().skip(int(0.5*total_docs)):
        db.testing.save(doc, safe=True)

    classes = list(set([d['field'] for d in db.theses.find({}, {'field': 1})]))
    voc, prior, cond = train(classes, db.training)

    print 'Vocabulary: ', len(voc)
    print 'Prior:', prior
    print 'Cond.:', cond
