#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy
import tempfile
import subprocess

import sys
import os
import os.path
import time
import cStringIO as StringIO

from pymongo import Connection

from bag import tokenize, bag_of_words

db = Connection().theses

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

    cut = (numpy.max(f.values()) + numpy.mean(f.values()))/2.0
    return dict(filter(lambda n: n[1] >= cut, f.iteritems()))

def term_count_naive(vocabulary, textfile):
    nterm = dict.fromkeys(vocabulary, 0)
    for term in textfile.getvalue().split():
        if term in vocabulary:
            nterm[term] += 1
    return nterm

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

        a = time.time()
        print '  Joining all class docs...',
        textfile = StringIO.StringIO()
        for doc in docs.find({'field': cls}):
            if not data_valid(doc): continue
            textfile.write((' '.join(tokenize(doc['data'])) + ' ').encode('utf-8', 'replace'))
        print 'took %.4f secs to write.' % (time.time() - a)

        a = time.time()
        s = textfile.getvalue()
        print 'took %.4f secs to retrieve string.' % (time.time() - a)

        #nterm = term_count_bruteforce(vocabulary, textfile)
        a = time.time()
        nterm = term_count_naive(vocabulary, textfile)
        print 'took %.4f secs to count.' % (time.time() - a)

        print '  Computing conditional probabilities...',
        for term in vocabulary:
            if term not in cond:
                cond[term] = {}
            if cls not in cond[term]:
                cond[term][cls] = {}
            cond[term][cls] = (nterm[term] + 1)/float(sum([t + 1 for t in nterm.values()]))
        print 'Done'
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

    open('training_result.py', 'w').write(('vocabulary=%s\nprior=%s\ncond=%s\n' % (voc, prior, cond)).encode('utf-8', 'replace'))