#!/usr/bin/env python
# encoding: utf-8
"""
Object Oriented Abstraction of a latex document

2014-12-02 - Created by Jonathan Sick
"""

import codecs

from .gitio import read_git_blob
from . import texutils


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

    def remove_comments(self):
        """Remove latex comments from document (modifies document in place)."""
        self.text = texutils.remove_comments(self.text)


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

    Parameters
    ----------
    git_path : str
        Path to the document in the git repository, relative to the root
        of the repository.
    git_hash : str
        Any SHA or git tag that can resolve into a commit in the
        git repository.
    root : str
        Path from current working directory to the root of the git repository.
    """
    def __init__(self, git_path, git_hash, root='.'):
        # read teh tex document
        self._git_path = git_path
        self._git_root = root
        self._git_hash = git_hash
        text = read_git_blob(git_hash, git_path, root=root)
        super(GitTexDocument, self).__init__(text)
