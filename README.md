About
=====

This is the result of my thesis for graduating on Electrical Engineering. It is a simple classification system with
the following specs:

* Naive Bayes classifier - algorithms are modified versions of [Manning et. al.](http://nlp.stanford.edu/IR-book/)
* Document Frequency (DF) feature selection - [Yiming Yang](http://net.pku.edu.cn/~course/cs502/2003/031119/yang97comparative.pdf)
* Web scraping framework (built upon scrapy) which uses Document Frequency feature selection.

Objective
---------
This classification system's objective is to classify a thesis on its respective field of knowledge.

Experimental Setup
------------------

The system was subject to the following experiment:

* 647 theses were downloaded from [Digital Library - USP](http://www.teses.usp.br/), which is a thesis database for the Universidade de São Paulo
* Courses were chosen at random
* 75% used for training (chosen at random)
* 25% used for testing
* Objective: observe the relationship between the number of features and the output global accuracy

Results
-------
By increasing the number of features, it was observed that the accuracy increases monotonically, as expected. The
full results are shown in the final document (tcc.pdf).

This system achieved 84.66% global accuracy when using 12359 features. Even with this huge number of features and a
relatively big document space, it still achieved considerable speed, where training took 50 secs, classifying 20 secs
and extracting features 40 secs (total 110 secs all steps).

Concerning processing, training and classification throughput figures were respectively 280k words
per sec and 1.6k words per sec.

Repeating the Experiment
------------------------

If you're interested in repeating it or learning from it, feel free to contact me.


Requirements
============

* [Python 2.6+](http://python.org)
* [Scrapy 0.12](http://scrapy.org/)
* [matplotlib 1.0.1](http://matplotlib.sourceforge.net/)
* [numpy 2.5.1](numpy.scipy.org/)
* [MongoDB 1.8.3](www.mongodb.org)
* [Pymongo](http://api.mongodb.org/python/current/)
