# -*- coding: utf-8 -*-
import numpy
import logging

import bag
import database

from database import db
from classifiers import NaiveBayesClassifier

log = logging.getLogger(__file__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(filename)s:%(funcName)s(%(lineno)d)\t%(message)s', datefmt='%H:%M:%S')

class Experiment(NaiveBayesClassifier):

    def __init__(self, ratio=0.5):
        self.ratio = ratio
        classes = database.get_classes()
        super(Experiment, self).__init__(classes, *self.build_experiment(classes))

    def run(self):
        self.features = self.select_features()
        self.train()
        self.test()

    def test(self):
        stats = dict.fromkeys(self.classes)
        success = 0.0
        errors = 0.0
        for k in stats:
            stats[k] = {'tp': 0 , 'fp': 0, 'fn': 0, 'tn': 0}

        for doc in self.testing_docs.find():
            if not database.doc_has_data(doc):
                continue

            cls = self.classify(doc)
            if doc['field'] == cls:
                success += 1
                stats[cls]['tp'] += 1
                log.debug('Success (%s/%s)', doc['author'], doc['field'])
            else:
                errors += 1

                # doc['field'] is the correct label, cls is wrong.
                # Account a false positive at the correct label: doc['field']
                stats[doc['field']]['fp'] += 1

                # Account a false negative: cls
                stats[cls]['fn'] += 1
                log.debug('Error (%s/%s)', doc['author'], doc['field'])

        log.debug(stats)

        for cls, stat in stats.iteritems():
            log.info('Class %s (tp=%d,fp=%d,fn=%d,tn=%d)', cls, stat['tp'], stat['fp'], stat['fn'], stat['tn'])
            precision = stat['tp']/float(stat['tp'] + stat['fp'])
            recall = stat['tp']/float(stat['tp'] + stat['fn'])
            f1 = 2.0 * precision * recall / (precision + recall)

            log.debug('\tPrecision=%.3f, Recall=%.3f, F1=%.3f', precision, recall, f1)

        log.info('Global accuracy: %.2f %%', 100.0 * success/float(success + errors))

    def build_experiment(self, classes):
        """ Builds the experiment set by assigning half of the available documents for training
        and the other half for testing. This is stupid and should be changed.
        """
        log.info("building experiment..")

        count = {}
        ratio = self.ratio

        db.training.drop()
        db.testing.drop()

        db.training.ensure_index('field')
        db.testing.ensure_index('field')

        log.debug('classes accounting:')
        for cls in classes:
            count[cls] = db.theses.find({'field': cls, 'data': {'$exists': True}}).count()
            log.debug('\t%s\t%d', cls, count[cls])

        for cls in classes:
            for doc in db.theses.find({'field': cls, 'data': {'$exists': True}}).limit(int(ratio * count[cls])):
                db.training.save(doc, safe=True)
            for doc in db.theses.find({'field': cls, 'data': {'$exists': True}}).skip(int(ratio * count[cls])):
                db.testing.save(doc, safe=True)

        log.info('built experiment, train/test per class document ratio: %.2f', ratio)
        return (db.training, db.testing)

    def select_features(self):
        """ Select most frequent terms.
        """
        log.info('selecting features..')

        f = {}
        for doc in self.training_docs.find():
            if not database.doc_has_data(doc):
                continue

            for term in bag.bag_of_words(doc['data']):
                f.setdefault(term, 1)
                f[term] += 1

        cut = (numpy.max(f.values()) + numpy.mean(f.values()))/8.0
        higher = dict(filter(lambda n: n[1] >= cut, f.iteritems()))
        log.info('selected %d terms', len(higher))
        return higher

def run():
    Experiment().run()

if __name__ == '__main__':
    run()
