#!/usr/bin/env python
# encoding: utf-8

import os
import re
from setuptools import setup


def rel_path(path):
    return os.path.join(os.path.dirname(__file__), path)


def get_version():
    with open(rel_path(os.path.join("paperweight", "__init__.py"))) as f:
        for line in f:
            if line.startswith("VERSION"):
                version = re.findall(r'\"(.+?)\"', line)[0]
                return version
    return "0.0.0.dev"


try:
    long_description = open(rel_path('README.rst'), 'rt').read()
except IOError:
    long_description = ''

setup(
    name='paperweight',
    version='0.0',
    author='Jonathan Sick',
    author_email='jonathansick@mac.com',
    license='BSD',
    description='Tools for hacking LaTeX documents',
    long_description=long_description,
    py_modules=['paperweight']
)
