# -*- coding: utf-8 -*-
from pymongo import Connection

db = Connection().theses

def get_classes():
    """ Return available classes on theses database.
    """
    return list(set([d['field'] for d in db.theses.find({}, {'field': 1})]))

def doc_has_data(doc):
    """ Returns whether the document has non-empty data.
    """
    return True if 'data' in doc and len(doc['data']) > 0 else False

