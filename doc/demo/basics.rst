
Paperweight Basics
==================

This guide provides a brief demo of what you can do with Paperweight.
Here we'll use a LaTeX document that I have handy, but you may want to
try the same commands on your own papers. There are some issues
typesetting ipython notebooks on Read The Docs, so you may prefer to
`view this notebook with the ipython notebook
viewer <http://nbviewer.ipython.org/github/jonathansick/paperweight/blob/master/doc/demo/basics.ipynb>`__.

First, let's set our current working directory to match the paper for
convenience.

.. code:: python

    from pprint import pprint
    import os
    os.chdir("/Users/jsick/Dropbox/m31/writing/skysubpub")
    !rm embedded_demo.tex

.. parsed-literal::

    rm: embedded_demo.tex: No such file or directory


If you're processing TeX documents in an automated fashion, you might
not know *a priori* what file contains the root of a LaTeX document. By
*root* we mean the file with a ``'\documentclass'`` declaration.
Paperweight provides an API to find this. (Note that
``find_root_tex_document()`` can accept a directory path as an argument,
so you are not restricted to the current working directory)

.. code:: python

    from paperweight import texutils
    root_tex_path = texutils.find_root_tex_document()
    print(root_tex_path)

.. parsed-literal::

    ./skysub.tex


Working with LaTeX Documents
----------------------------

Now that we know where our LaTeX document is, we can open it as a
``FilesystemTexDocument``. Note we also provide a ``GitTexDocument``
class to work with documents stored in an arbitrary commit within a git
repo. We'll get to that in a separate demo.

.. code:: python

    from paperweight.document import FilesystemTexDocument
    doc = FilesystemTexDocument(root_tex_path)
With a ``FilesystemTexDocument`` you can ask questions about the
document, such as what BibTeX file it uses:

.. code:: python

    print(doc.bib_name)
    print(doc.bib_path)

.. parsed-literal::

    master.bib
    /Users/jsick/Library/texmf/bibtex/bib/master.bib


or what the names and word-count locations of the sections are:

.. code:: python

    doc.sections



.. parsed-literal::

    [(908, u'Introduction'),
     (2601, u'Observations'),
     (4641, u'Image Preparation'),
     (6186, u'Sky Flat Fielding and Median Sky Subtraction'),
     (7762, u'Photometric calibration'),
     (8317, u'Analysis of Sky Flat Fielding and Background Subtraction Methods'),
     (12500, u'Sky Offset Optimization'),
     (14284, u'Analysis of Scalar Sky Offsets'),
     (17032, u'Systematic Uncertainties in Surface Brightness Reconstruction'),
     (18456, u'Conclusions')]



or what other tex files it includes using ``\input{}`` commands:

.. code:: python

    doc.find_input_documents()



.. parsed-literal::

    [u'tables/nightset_medsky_offset_hierarchy.tex',
     u'tables/nightset_medsky_scalar_resid_diffs.tex']



We can manipulate our LaTeX document too. For instance, we can embed the
input TeX files and bibliography directly into the main text body:

.. code:: python

    doc.inline_inputs()
    doc.inline_bbl()
Now you'll see that we no longer reference other tex files or a bibtex
file since all text content is embedded into the root TeX document. This
can be handy for submitting the article to a journal (in fact the
`preprint <http://github.com/jonathansick/preprint>`__ tool uses
Paperweight to do just that).

.. code:: python

    print(doc.find_input_documents())
    print(doc.bib_name)

.. parsed-literal::

    []
    None


We can delete comments from the LaTeX source as well. When we do that
you'll notice that the sections now appear at earlier word count
locations.

.. code:: python

    doc.remove_comments()
.. code:: python

    doc.sections



.. parsed-literal::

    [(812, u'Introduction'),
     (2505, u'Observations'),
     (4365, u'Image Preparation'),
     (5530, u'Sky Flat Fielding and Median Sky Subtraction'),
     (7011, u'Photometric calibration'),
     (7548, u'Analysis of Sky Flat Fielding and Background Subtraction Methods'),
     (10809, u'Sky Offset Optimization'),
     (12497, u'Analysis of Scalar Sky Offsets'),
     (14942, u'Systematic Uncertainties in Surface Brightness Reconstruction'),
     (16082, u'Conclusions')]



You can easily write the modified TeX source back to the filesystem with
the ``write()`` method:

.. code:: python

    doc.write("embedded_demo.tex")
Extracting Citation Information
-------------------------------

One of the goals of Paperweight is to allow us to *understand* our
scientific documents. A big part of that is understanding how we cite
other papers.

With our document, we can ask for what references are made in the
document according to the cite keys used in ``\cite*{}`` commands:

.. code:: python

    doc.bib_keys



.. parsed-literal::

    [u'Saglia:2010',
     u'Courteau:2014',
     u'Courteau:2011',
     u'Athanassoula:2006',
     u'Nelder:1965',
     u'de-Jong:1996b',
     u'Maraston:1998',
     u'Marigo:2008',
     u'Conroy:2010b',
     u'Barmby:2006',
     u'Pforr:2012',
     u'Maraston:2005',
     u'Maraston:2006',
     u'Williams:2003',
     u'Williams:2002',
     u'Bruzual:2007',
     u'Brown:2009a',
     u'Press:2007',
     u'Olsen:2006',
     u'Bertin:2002',
     u'McConnachie:2005',
     u'McConnachie:2009',
     u'Bertin:1996',
     u'Bertin:2006',
     u'Brown:2008',
     u'Adams:1996',
     u'Dalcanton:2012',
     u'Brown:2003',
     u'Dutton:2005',
     u'Sick:2013a',
     u'Marmo:2008',
     u'Massey:2006',
     u'Irwin:2005',
     u'Skrutskie:2006',
     u'MacArthur:2004',
     u'Conroy:2013',
     u'Ibata:2005',
     u'Berriman:2008',
     u'Kormendy:2004',
     u'Taylor:2011',
     u'Beaton:2007',
     u'Puget:2004',
     u'Brown:2006',
     u'Vaduvescu:2004',
     u'Worthey:2005']



This is useful, but we can go deeper by understanding the context in
which these works are cited. To do this we can use the
``extract_citation_context()`` method to generate a dictionary, keyed by
bib keys, of all citation instances in the document. In this example
paper I've cited 45 works:

.. code:: python

    cites = doc.extract_citation_context()
    print(len(cites))

.. parsed-literal::

    45


Each entry in the ``cites`` dictionary is a list of specific occurences
where that work was cited. Thus its easy to count the number of times
each work was cited:

.. code:: python

    for cite_key, instances in cites.iteritems():
        print("{0} cited {1:d} time(s)".format(cite_key, len(instances)))

.. parsed-literal::

    Saglia:2010 cited 1 time(s)
    Courteau:2014 cited 2 time(s)
    Courteau:2011 cited 1 time(s)
    Athanassoula:2006 cited 1 time(s)
    Nelder:1965 cited 1 time(s)
    de-Jong:1996b cited 1 time(s)
    Maraston:1998 cited 1 time(s)
    Marigo:2008 cited 1 time(s)
    Conroy:2010b cited 1 time(s)
    Barmby:2006 cited 5 time(s)
    Pforr:2012 cited 1 time(s)
    Maraston:2005 cited 1 time(s)
    Maraston:2006 cited 1 time(s)
    Williams:2003 cited 1 time(s)
    Williams:2002 cited 1 time(s)
    Bruzual:2007 cited 1 time(s)
    Brown:2009a cited 1 time(s)
    Press:2007 cited 1 time(s)
    Olsen:2006 cited 1 time(s)
    Bertin:2002 cited 1 time(s)
    McConnachie:2005 cited 1 time(s)
    McConnachie:2009 cited 1 time(s)
    Bertin:1996 cited 2 time(s)
    Bertin:2006 cited 1 time(s)
    Brown:2008 cited 1 time(s)
    Adams:1996 cited 4 time(s)
    Dalcanton:2012 cited 2 time(s)
    Brown:2003 cited 1 time(s)
    Dutton:2005 cited 1 time(s)
    Sick:2013a cited 1 time(s)
    Marmo:2008 cited 1 time(s)
    Massey:2006 cited 1 time(s)
    Irwin:2005 cited 1 time(s)
    Skrutskie:2006 cited 2 time(s)
    MacArthur:2004 cited 1 time(s)
    Conroy:2013 cited 1 time(s)
    Ibata:2005 cited 1 time(s)
    Berriman:2008 cited 2 time(s)
    Kormendy:2004 cited 1 time(s)
    Taylor:2011 cited 1 time(s)
    Beaton:2007 cited 2 time(s)
    Puget:2004 cited 2 time(s)
    Brown:2006 cited 1 time(s)
    Vaduvescu:2004 cited 7 time(s)
    Worthey:2005 cited 1 time(s)


It looks like I've cited ``Vaduvescu:2004`` a lot. Lets look at where it
was cited:

.. code:: python

    print([c['section'] for c in cites['Vaduvescu:2004']])

.. parsed-literal::

    [(812, u'Introduction'), (2505, u'Observations'), (2505, u'Observations'), (2505, u'Observations'), (7548, u'Analysis of Sky Flat Fielding and Background Subtraction Methods'), (7548, u'Analysis of Sky Flat Fielding and Background Subtraction Methods'), (12497, u'Analysis of Scalar Sky Offsets')]


In the list above, the first item lists the cumulative word count where
the section starts, while the second item is the name of the section.

There's a lot of other information associated with each citation
instance. Here's metadata associated with the first reference to
``Vaduvescu:2004``:

.. code:: python

    pprint(cites['Vaduvescu:2004'][0])

.. parsed-literal::

    {'position': 2235,
     'section': (812, u'Introduction'),
     'wordsafter': u'also found detector systems , case ( decommissioned ) CFHT - IR camera , add time - varying background signal',
     'wordsbefore': u'Spatial structures NIR sky leave residual shapes background subtracted disk images ultimately affect ability produce seamless NIR mosaic M31 .'}


