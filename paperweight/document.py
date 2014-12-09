#!/usr/bin/env python
# encoding: utf-8
"""
Object Oriented Abstraction of a latex document

2014-12-02 - Created by Jonathan Sick
"""

import os
from collections import OrderedDict
from itertools import chain
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
        self._children = OrderedDict()

    def find_input_documents(self):
        """Find all tex documents input by this root document.

        Returns
        -------
        paths : list
            List of filepaths for input documents. Paths are relative
            to the document (i.e., as written in the latex document).
        """
        paths = []
        itr = chain(texutils.input_pattern.finditer(self.text),
                    texutils.input_ifexists_pattern.finditer(self.text))
        for match in itr:
            fname = match.group(1)
            if not fname.endswith('.tex'):
                full_fname = ".".join((fname, 'tex'))
            else:
                full_fname = fname
            paths.append(full_fname)
        return paths

    @property
    def bib_name(self):
        """Find and return the name of the bibtex bibliography file."""
        bib_name = None
        for match in texutils.bib_pattern.finditer(self.text):
            bib_name = match.group(1)
            if not bib_name.endswith('.bib'):
                bib_name = ".".join((bib_name, "bib"))
        return bib_name

    @property
    def bib_path(self):
        """Return the full file path to the .bib bibliography document."""
        bib_name = self.bib_name
        # FIXME need to bake in search paths for tex documents in all platforms
        osx_path = os.path.expanduser(
            "~/Library/texmf/bibtex/bib/{0}".format(bib_name))
        if self._file_exists(bib_name):
            return bib_name  # bib is in project directory
        elif os.path.exists(osx_path):
            return osx_path
        else:
            return None

    def remove_comments(self, recursive=True):
        """Remove latex comments from document (modifies document in place)."""
        self.text = texutils.remove_comments(self.text)
        if recursive:
            for path, document in self._children.iteritems():
                document.remove_comments(recursive=True)

    @property
    def bib_keys(self):
        """List of all bib keys in the document (and inputted documents)."""
        bib_keys = []
        # Get bib keys in this document
        for match in texutils.cite_pattern.finditer(self.text):
            keys = match.group(1).split(',')
            bib_keys += keys
        # Recursion
        for path, document in self._children.iteritems():
            bib_keys += document.bib_keys
        bib_keys = list(set(bib_keys))
        return bib_keys

    def write(self, path):
        """Write the document's text to a ``path`` on the filesystem."""
        with codecs.open(path, 'w', encoding='utf-8') as f:
            f.write(self.text)

    @property
    def bibitems(self):
        """List of bibitem strings appearing in the document."""
        bibitems = []
        lines = self.text.split('\n')
        for i, line in enumerate(lines):
            if line.lstrip().startswith(u'\\bibitem'):
                # accept this line
                # check if next line is also part of bibitem
                # FIXME ugh, re-write
                j = 1
                while True:
                    try:
                        if (lines[i + j].startswith(u'\\bibitem') is False) \
                                and (lines[i + j] != '\n'):
                            line += lines[i + j]
                        elif "\end{document}" in lines[i + j]:
                            break
                        else:
                            break
                    except IndexError:
                        break
                    else:
                        print line
                        j += 1
                print "finished", line
                bibitems.append(line)
        return bibitems


class FilesystemTexDocument(TexDocument):
    """A tex document derived from a file in the filesystem.

    Parameters
    ----------
    filepath : unicode
        Path to the '.tex' on the filesystem.
    recursive : bool
        If `True` (default), then tex documents input by this root document
        will be opened.
    """
    def __init__(self, path, recursive=True):
        # read the tex document
        self._filepath = path
        with codecs.open(path, 'r', encoding='utf-8') as f:
            text = f.read()
        super(FilesystemTexDocument, self).__init__(text)
        if recursive:
            child_paths = self.find_input_documents()
            for path in child_paths:
                # FIXME may need to deal with path normalization here.
                self._children[path] = FilesystemTexDocument(path,
                                                             recursive=True)

    def _file_exists(self, path):
        return os.path.exists(path)

    def inline_bbl(self):
        """Inline a compiled bibliography (.bbl) in place of a bibliography
        environment. The document is modified in place.
        """
        bbl_path = os.path.splitext(self._filepath)[0] + ".bbl"
        if not os.path.exists(bbl_path):
            return
        with codecs.open(bbl_path, 'r', encoding='utf-8') as f:
            bbl_text = f.read()
        self.text = texutils.inline_bbl(self.text, bbl_text)

    def inline_inputs(self):
        """Inline all input latex files references by this document. The
        inlining is accomplished recursively.
        """
        self.text = texutils.inline(self.text)


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
    def __init__(self, git_path, git_hash, root='.', recursive=True):
        # read teh tex document
        self._git_path = git_path
        self._git_root = root
        self._git_hash = git_hash
        text = read_git_blob(git_hash, git_path, root=root)
        super(GitTexDocument, self).__init__(text)
        if recursive:
            child_paths = self.find_input_documents()
            for path in child_paths:
                # FIXME may need to deal with path normalization here.
                self._children[path] = FilesystemTexDocument(path,
                                                             recursive=True)

    def _file_exists(self, path):
        return False  # TODO need to implement file existence test in git
