#!/usr/bin/env python
# encoding: utf-8
"""
Utility functions for working with NLTK

2014-12-09 - Created by Matthew Sottile
"""

import nltk

def wordify(text):
    stopset = set(nltk.corpus.stopwords.words('english'))
    stemmer = nltk.PorterStemmer()
    return nltk.WordPunctTokenizer().tokenize(text)
