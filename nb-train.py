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
    """ Returns whether the document has non-empty data.
    """
    return True if 'data' in doc and len(doc['data']) > 0 else False

def extract_vocabulary(docs):
    """ Extract whole vocabulary from documents.
    """
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

def term_count_naive(vocabulary, text):
    """ Counts all occurrences of vocabulary words on the given text.

    This simplified method simply slides through all the text words
    accounting for vocabulary words.
    """
    nterm = dict.fromkeys(vocabulary, 0)
    for term in text.split():
        if term in vocabulary:
            nterm[term] += 1
    return nterm

def train(classes, docs):
    """ Performs a naive-bayes training for the classes using the given docs.
    'docs' parameter is expected to be a pymongo collection and classes a
    list of classes present on the documents.

    Returns a tuple (vocabulary, prior probabilities, conditional probabilities)
    which defines the classifier (see nb-classify.py).
    """
    n = docs.count()
    prior = {}
    cond = {}

    vocabulary = extract_vocabulary(docs)

    for cls in classes:
        # Compute prior probabilities
        nc = docs.find({'field': cls}).count()
        prior[cls] = nc/float(n)

        # Join all documents
        textfile = StringIO.StringIO()
        for doc in docs.find({'field': cls}):
            if not data_valid(doc): continue
            textfile.write((' '.join(tokenize(doc['data'])) + ' ').encode('utf-8', 'replace'))

        # Count vocabulary occurences on joined documents
        nterm = term_count_naive(vocabulary, textfile.getvalue())

        # Compute conditional probabilities
        for term in vocabulary:
            if term not in cond:
                cond[term] = {}
            if cls not in cond[term]:
                cond[term][cls] = {}
            cond[term][cls] = (nterm[term] + 1)/float(sum([t + 1 for t in nterm.values()]))
    return vocabulary, prior, cond

def build_experiment():
    """ Builds the experiment set by assigning half of the available documents for training
    and the other half for testing. This is stupid and should be changed.
    """
    total_docs = db.theses.count()
    training_docs = db.theses.find().limit(int(0.5*total_docs))

    for doc in training_docs:
        db.training.save(doc, safe=True)

    for doc in db.theses.find().skip(int(0.5*total_docs)):
        db.testing.save(doc, safe=True)

if __name__ == '__main__':
    # Uncomment the following line the first time you run this.
    #build_experiment()

    classes = list(set([d['field'] for d in db.theses.find({}, {'field': 1})]))

    print 'Training...',
    voc, prior, cond = train(classes, db.training)
    print ' done (vocabulary=%d words)' % len(voc)

    print 'Saving results to training_result.py...',
    open('training_result.py', 'w').write(('vocabulary=%s\nprior=%s\ncond=%s\n' % (voc, prior, cond)).encode('utf-8', 'replace'))
    print ' done.'
