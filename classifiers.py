#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import numpy
import operator
import logging

import cStringIO as StringIO

import database

from bag import *

log = logging.getLogger(__file__)

class NaiveBayesClassifier(object):

    def __init__(self, classes, training_docs, testing_docs):
        self.classes = classes
        self.training_docs = training_docs
        self.testing_docs = testing_docs
        self.prior = {}
        self.cond = {}
        self._features = []

    @property
    def features(self):
        return self._features

    @features.setter
    def features(self, features):
        self._features = features

    def train(self):
        """ Performs a naive-bayes on the given features. Fills out
        dictionaries prior and cond with prior probabilities
        P(c) of a class 'c' and conditional P(term|c).
        """
        docs = self.training_docs
        n = docs.count()
        prior = {}
        cond = {}
        memo = {}

        log.debug('starting training on %d documents..', n)
        start_time = time.time()

        for cls in self.classes:
            # Compute prior probabilities
            nc = docs.find({'field': cls}).count()

            # Maximum Likelihood Estimate (MLE)
            prior[cls] = numpy.log(nc/float(n))

            # Join all documents for faster counting
            textfile = StringIO.StringIO()
            for doc in docs.find({'field': cls}):
                if not database.doc_has_data(doc):
                    continue
                textfile.write((' '.join(tokenize(doc['data'])) + ' ').encode('utf-8', 'replace'))

            # Count vocabulary occurences on joined documents
            nterm = dict.fromkeys(self.features, 0)
            for term in textfile.getvalue().split():
                if term in self.features:
                    nterm[term] += 1

            # Precompute denominator for conditional prob. estimator
            base = float(sum(nterm.values()) + len(nterm))

            # Compute conditional probabilities
            for term in self.features:
                if term not in cond:
                    cond[term] = {}
                val = (nterm[term] + 1)/base
                if val not in memo:
                    memo[val] = numpy.log(val)

                cond[term][cls] = memo[val]

        log.debug('finished training (took %.3f secs)', time.time() - start_time)

        self.prior = prior
        self.cond = cond

    def classify(self, doc):
        """ Classify the input document 'doc'.
        """
        tokens = tokenize_map(doc['data'])
        score = {}

        for cls in self.classes:
            score[cls] = self.prior[cls]

        for term, count in tokens.iteritems():
            if term not in self.cond:
                continue
            for cls in self.classes:
                score[cls] += count * self.cond[term][cls]

        return max(score.iteritems(), key=operator.itemgetter(1))[0]

