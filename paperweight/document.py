#!/usr/bin/env python
# encoding: utf-8
"""
Object Oriented Abstraction of a latex document

2014-12-02 - Created by Jonathan Sick
"""

import codecs

from .gitio import read_git_blob


class TexDocument(object):
    """Baseclass for a tex document.

    Parameters
    ----------
    text : unicode
        Unicode-encoded text of the latex document.

    Attributes
    ----------
    text : unicode
        Text of the document as a unicode string.
    """
    def __init__(self, text):
        super(TexDocument, self).__init__()
        self.text = text


class FilesystemTexDocument(TexDocument):
    """A tex document derived from a file in the filesystem.

    Parameters
    ----------
    filepath : unicode
        Path to the '.tex' on the filesystem.
    """
    def __init__(self, path):
        # read the tex document
        self._filepath = path
        with codecs.open(path, 'r', encoding='utf-8') as f:
            text = f.read()
        super(FilesystemTexDocument, self).__init__(text)


class GitTexDocument(TexDocument):
    """A tex document derived from a file in the git repository.

    .. note:: Should I include the path to the git root? (in case the user's
              CWD is not that of the git document)
    """
    def __init__(self, git_path, git_hash):
        # read teh tex document
        self._git_path = git_path
        self._git_hash = git_hash
        text = read_git_blob(git_hash, git_path)
        super(GitTexDocument, self).__init__(text)
