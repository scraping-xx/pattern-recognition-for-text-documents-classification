About
=====

This is the result of my thesis for graduating on Electrical Engineering. It's a classification system with
the following specs:
* naive bayes classifier (algorithms are modified versions of Manning et. al. (http://nlp.stanford.edu/IR-book/))
* document frequency (DF) feature selection (see http://net.pku.edu.cn/~course/cs502/2003/031119/yang97comparative.pdf A Comparative Study on Feature Selection in Text Categorization. Yiming Yang)
* simple web scraping framework (built upon scrapy) which uses Document Frequency feature selection.

Requirements
============

* Python 2.6+   - www.python.org
* Scrapy
* pylab
* MongoDB 1.8.3 - www.mongodb.org
* Pymongo       - http://api.mongodb.org/python/current/ (install with easy_install)
