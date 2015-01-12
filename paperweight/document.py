#!/usr/bin/env python
# encoding: utf-8
"""
Object oriented access to LaTeX documents.

The :mod:`paperweight.document` module provides object-oriented interfaces
for manipulating or mining LaTeX documents.
Much of the functionality of the :mod:`paperweight.texutils`,
:mod:`paperweight.gitio` and :mod:`paperweight.nlputils` modules can be
accessed through this interface.

Depending on how the LaTeX document is stored, you should use either of two
document classes.
:class:`paperweight.document.FilesystemTexDocument` should be used for regular
documents in the filesystem.
If you wish to operate on documents stored within a certain commit of a
checked-out Git repository, then use
:class:`paperweight.document.GitTexDocument`.
The interfaces for both classes are consistent since they inherit from
:class:`paperweight.document.TexDocument` under the hood.
"""

import os
from collections import OrderedDict, defaultdict
from itertools import chain
import codecs

from .gitio import read_git_blob
from . import texutils, nlputils


__all__ = ['FilesystemTexDocument', 'GitTexDocument', 'TexDocument']


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
        self.sections
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
    def sections(self):
        """List with tuples of section names and positions.
        Positions of section names are measured by cumulative word count.
        """
        sections = []

        for match in texutils.section_pattern.finditer(self.text):
            textbefore = self.text[0:match.start()]
            wordsbefore = nlputils.wordify(textbefore)
            numwordsbefore = len(wordsbefore)
            sections.append((numwordsbefore, match.group(1)))

        self._sections = sections
        return sections

    @property
    def bib_name(self):
        """Name of the BibTeX bibliography file (e.g.,
        ``'mybibliography.bib'``).
        """
        bib_name = None
        for match in texutils.bib_pattern.finditer(self.text):
            bib_name = match.group(1)
            if not bib_name.endswith('.bib'):
                bib_name = ".".join((bib_name, "bib"))
        return bib_name

    @property
    def bib_path(self):
        """Absolute file path to the .bib bibliography document."""
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
        """Remove latex comments from document (modifies document in place).

        Parameters
        ----------
        recursive : bool
            Remove comments from all input LaTeX documents (default ``True``).
        """
        self.text = texutils.remove_comments(self.text)
        if recursive:
            for path, document in self._children.iteritems():
                document.remove_comments(recursive=True)

    @property
    def bib_keys(self):
        """List of all bib keys in the document (and input documents)."""
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

    def extract_citation_context(self, n_words=20):
        """Generate a dictionary of all bib keys in the document (and input
        documents), with rich of metadata about the context of each
        citation in the document.

        For example, suppose ``'Sick:2014'`` is cited twice within a document.
        Then the dictionary returned by this method will have a length-2
        list under the ``'Sick:2014'`` key. Each item in this list
        will be a dictionary providing metadata of the context for that
        citation. Fields of this dictionary are:

        - ``position``: (int) the cumulative word count at which the
          citation occurs.
        - ``wordsbefore``: (unicode) text occuring before the citation.
        - ``wordsafter``: (unicode) text occuring after the citation.
        - ``section``: (unicode) name of the section in which the citation
          occurs.

        Parameters
        ----------
        n_words : int
            Number of words before and after the citation to extract for
            context.

        Returns
        -------
        bib_keys : dict
            Dictionary, keyed by BibTeX cite key, where entires are lists
            of instances of citations. See above for the format of the
            instance metadata.
        """
        bib_keys = defaultdict(list)
        # Get bib keys in this document
        for match in texutils.cite_pattern.finditer(self.text):

            textbefore = self.text[0:match.start()]
            textafter = self.text[match.end():-1]

            wordsbefore = nlputils.wordify(textbefore)
            wordsafter = nlputils.wordify(textafter)
            numwordsbefore = len(wordsbefore)
            # numwordsafter = len(wordsafter)

            containing_section = None
            for (section_pos, section_name) in self._sections:
                if section_pos < numwordsbefore:
                    containing_section = (section_pos, section_name)

            citebody = match.groups()
            keys = (citebody[-1].replace(" ", "")).split(',')
            for key in keys:
                cite_instance = {
                    "position": numwordsbefore,
                    "wordsbefore": (" ".join(wordsbefore[-n_words:])),
                    "wordsafter": (" ".join(wordsafter[:n_words])),
                    "section": containing_section}
                bib_keys[key] += [cite_instance]

        # Recursion
        for path, document in self._children.iteritems():
            sub_bib_keys = document.rich_bib_keys(n_words=n_words)
            for k, cite_instances in sub_bib_keys.iteritems():
                bib_keys[k] += cite_instances

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
    """A TeX document derived from a file in the filesystem.

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
        self._filepath = os.path.abspath(path)
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
        try:
            with codecs.open(bbl_path, 'r', encoding='utf-8') as f:
                bbl_text = f.read()
        except IOError:
            print("Cannot open bibliography {0}".format(bbl_path))
        self.text = texutils.inline_bbl(self.text, bbl_text)

    def inline_inputs(self):
        """Inline all input latex files references by this document. The
        inlining is accomplished recursively. The document is modified
        in place.
        """
        self.text = texutils.inline(self.text,
                                    os.path.dirname(self._filepath))
        # Remove children
        self._children = {}


class GitTexDocument(TexDocument):
    """A tex document derived from a file in the git repository.

    .. todo:: This class is not fully implemented.

    Parameters
    ----------
    git_path : str
        Path to the document in the git repository, relative to the root
        of the repository.
    git_hash : str
        Any SHA or git tag that can resolve into a commit in the
        git repository.
    repo_dir : str
        Path from current working directory to the root of the git repository.
    """
    def __init__(self, git_path, git_hash, repo_dir='.', recursive=True):
        # read teh tex document
        self._git_path = git_path
        self._git_root = repo_dir
        self._git_hash = git_hash
        text = read_git_blob(git_hash, git_path, repo_dir=repo_dir)
        super(GitTexDocument, self).__init__(text)
        if recursive:
            child_paths = self.find_input_documents()
            for path in child_paths:
                # FIXME may need to deal with path normalization here.
                self._children[path] = FilesystemTexDocument(path,
                                                             recursive=True)

    def _file_exists(self, path):
        return False  # TODO need to implement file existence test in git
