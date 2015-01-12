Paperweight
===========

Paperweight is a Python package for hacking LaTeX documents.

Paperweight operates on LaTeX documents either on the local filesystem, or as a commit in a git repository.
Paperweight can be used to manipulate documents, such as embedded input files and bibliographies, or can provide analytics such as rich information about references made in a document.
See the API documentation below for further information.

Paperweight is `developed on GitHub <http://github.com/jonathansick/paperweight>`_ under an open BSD license.

Installation
------------

You can install the latest Paperweight and its dependencies from PyPI::

   pip install paperweight


You can also install the bleeding-edge from git::

   pip install git+git://github.com/jonathansick/paperweight.git


Alternatively you can develop directly on the git source repository::

   git clone https://github.com/jonathansick/paperweight.git
   cd paperweight
   python setup.py develop
   python setup.py build_sphinx


Documentation
-------------

.. toctree::
   :maxdepth: 2

   demo/index
   api/index


Indices
-------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


Contributors
------------

- `Jonathan Sick <http://github.com/jonathansick>`_
- `Matthew Sottile <http://github.com/mjsottile>`_

Paperweight was created as a hack for .Astronomy 6 (2014) in Chicago.
