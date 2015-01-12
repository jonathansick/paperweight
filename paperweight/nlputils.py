#!/usr/bin/env python
# encoding: utf-8
"""
Utility functions for working with NLTK
"""

import nltk


def wordify(text):
    """Generate a list of words given text, removing punctuation.

    Parameters
    ----------
    text : unicode
        A piece of english text.

    Returns
    -------
    words : list
        List of words.
    """
    stopset = set(nltk.corpus.stopwords.words('english'))
    tokens = nltk.WordPunctTokenizer().tokenize(text)
    return [w for w in tokens if w not in stopset]
