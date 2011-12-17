# -*- coding: utf-8 -*-
import time
import numpy
import logging
import datetime

import bag
import database

from database import db
from classifiers import NaiveBayesClassifier

log = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s:%(funcName)s(%(lineno)d)\t%(message)s', datefmt='%H:%M:%S')


class Experiment(NaiveBayesClassifier):

    def __init__(self, size_divider=4):
        self.size_divider = size_divider
        self.ratio = 0.75
        classes = database.get_classes()
        super(Experiment, self).__init__(classes, *self.build_experiment(classes))

    def run(self):
        self.features = self.select_features1()
        self.train()
        results = self.test()
        return results

    def test(self):
        stats = dict.fromkeys(self.classes)
        success = 0.0
        errors = 0.0
        for k in stats:
            stats[k] = {'tp': 0 , 'fp': 0, 'fn': 0, 'tn': 0}

        start = time.time()
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

        log.info("Took %.3f secs to classify", time.time() - start)
        info_stats = {}

        for cls, stat in stats.iteritems():
            log.info('Class %s (tp=%d,fp=%d,fn=%d,tn=%d)', cls, stat['tp'], stat['fp'], stat['fn'], stat['tn'])
            precision = stat['tp']/float(stat['tp'] + stat['fp'])
            try:
                recall = stat['tp']/float(stat['tp'] + stat['fn'])
                f1 = 2.0 * precision * recall / (precision + recall)
            except ZeroDivisionError:
                f1 = recall = 'nan'

            log.debug('\tPrecision=%.3f, Recall=%.3f, F1=%.3f', precision, recall, f1)

            info_stats[cls] = {}
            info_stats[cls]['precision'] = precision
            info_stats[cls]['recall'] = recall
            info_stats[cls]['f1'] = f1
            info_stats[cls]['features'] = len(self.features)

        global_accuracy = success/float(success + errors)

        log.info('Global accuracy: %.2f %%', global_accuracy * 100.0)
        info_stats['global_accuracy'] = global_accuracy

        return info_stats

    def build_experiment(self, classes):
        """ Builds the experiment set by assigning half of the available documents for training
        and the other half for testing. This is stupid and should be changed.
        """
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

        log.debug('building experiment..')
        start_time = time.time()

        trained = dict.fromkeys(classes, 0)
        test = dict.fromkeys(classes, 0)

        for cls in classes:
            docs = db.theses.find({'field': cls, 'data': {'$exists': True}})
            size = docs.count()
            indexes = range(size)
            numpy.random.shuffle(indexes)
            training = indexes[:int(ratio * count[cls])]
            i = 0
            for doc in docs:
                if i in training:
                    db.training.save(doc, safe=True)
                    trained[cls] += 1
                else:
                    db.testing.save(doc, safe=True)
                    test[cls] += 1
                i += 1

        log.debug('trained=%s, test=%s', str(trained), str(test))
        log.info('built experiment, train/test per class document ratio: %.2f (took %.3f secs)', ratio, time.time() - start_time)
        return (db.training, db.testing)


    def select_features(self):
        """ Select most frequent terms.
        """
        start_time = time.time()
        log.info('selecting features..')

        f = {}
        for doc in self.training_docs.find():
            if not database.doc_has_data(doc):
                continue

            for term in bag.bag_of_words(doc['data']):
                f.setdefault(term, 1)
                f[term] += 1

        cut = (numpy.max(f.values()) + numpy.mean(f.values()))/self.size_divider
        higher = dict(filter(lambda n: n[1] >= cut, f.iteritems()))
        log.info('selected %d terms (took %.3f secs)', len(higher), time.time() - start_time)
        return higher

    def select_features1(self):
        """ Select most frequent terms.
        """
        start_time = time.time()
        log.info('selecting features..')

        f = {}
        for doc in self.training_docs.find():
            if not database.doc_has_data(doc):
                continue

            for term in set(bag.bag_of_words(doc['data'])):
                f.setdefault(term, 1)
                f[term] += 1

        print 'Size: ', len(f)

        cut = (numpy.max(f.values()) + numpy.mean(f.values()))/self.size_divider
        higher = dict(filter(lambda n: n[1] >= cut, f.iteritems()))
        log.info('selected %d terms (took %.3f secs)', len(higher), time.time() - start_time)
        return higher


def run():
    import os.path
    data = {}

    dividers = range(2, 20, 2)
    for d in dividers:
        print 'Running experiment for divider=', d
        data[d] = Experiment(d).run()

    fname = 'feature_size_' + datetime.datetime.now().strftime('%Y%m%d%H%M') + '_results.py'
    path = os.path.join('results', fname)
    open(path, 'w').write('data=' + str(data))
    print 'Saved results to file:', path

if __name__ == '__main__':
    import cProfile
    import pstats

    cProfile.run('run()', 'profiling')
    p = pstats.Stats('profiling')
    p.sort_stats('time').print_stats(0.2)
