#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2017 Fabrice Laporte - kray.me
# The MIT License http://www.opensource.org/licenses/mit-license.php

import sys
from setuptools import setup

try:
    from semantic_release import setup_hook

    setup_hook(sys.argv)
except ImportError:
    pass

PKG_NAME = "qifqif"
DIRPATH = os.path.dirname(__file__)


def read_rsrc(filename):
    with codecs.open(os.path.join(DIRPATH, filename), encoding="utf-8") as _file:
        return _file.read().strip()


with codecs.open(os.path.join(PKG_NAME, "__init__.py"), encoding="utf-8") as fd:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE
    ).group(1)

setup(name=PKG_NAME,
    version=__version__,
    description='Enrich your QIF files with categories',
    long_description=open('README.md').read(),
    author='Fabrice Laporte',
    author_email='kraymer@gmail.com',
    url='https://github.com/KraYmer/qifqif',
    license='MIT',
    platforms='ALL',
    packages=['qifqif', ],
    entry_points={
        'console_scripts': [
            'qifacc = qifqif.qifacc:main',
            'qifqif = qifqif:main',
        ],
    },
    install_requires=['argparse', 'ordereddict', 'pyyaml'] + (
        ['pyreadline', 'colorama'] if sys.platform == 'win32' else
        ['blessed']) + (
        ['gnureadline'] if sys.platform == 'darwin' else []),
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Environment :: Console',
        'Topic :: Office/Business :: Financial :: Accounting'
    ]
)
