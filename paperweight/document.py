#!/usr/bin/env python
# encoding: utf-8
"""
Object Oriented Abstraction of a latex document

2014-12-02 - Created by Jonathan Sick
"""


class TexDocument(object):
    """Baseclass for a tex document.

    Parameters
    ----------
    text : unicode
        Unicode-encoded text of the latex document.
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
        text = None  # FIXME
        super(FilesystemTexDocument, self).__init__(text)


class GitTexDocument(TexDocument):
    """A tex document derived from a file in the git repository."""
    def __init__(self, git_path, git_hash):
        # read teh tex document
        self._git_path = git_path
        self._git_hash = git_hash
        text = None  # FIXME
        super(GitTexDocument, self).__init__(text)
