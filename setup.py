"""
Created on Sat Jan 19 09:08:25 2019

@author: gduscher
"""
# -*- coding: utf-8 -*-

from codecs import open
import os
import setuptools


here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    long_description = f.read()

with open(os.path.join(here, './version.py')) as f:
    __version__ = f.read().split("'")[1]


setuptools.setup(
    name="pycrosGUI",
    version=__version__,
    description="pyTEM: TEM Data Quantification library through a model-based approach",
    long_description=long_description,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Cython',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Scientific/Engineering :: Information Analysis'],
    keywords=['imaging', 'spectra', 'transmission', 'electron', 'microscopy',
              'scientific', 'scanning', 'eels', 'visualization', 'processing',
              'storage', 'hdf5', 'diffraction'],
    packages=setuptools.find_packages(exclude=["*.tests", "*.tests.*",
                                               "tests.*", "tests"]),
    url="https://pycroscopy.github.io/pycrosGUI/about.html",
    license='MIT',
    author="Gerd Duscher",
    author_email="gduscher@utk.edu",

    install_requires=['pyTEMlib', 'pyqt5', 'pyqtgraph'],  # 'PyQt5> 1.0'],#
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    platforms=['Linux', 'Mac OSX', 'Windows 11/10'],
    test_suite='pytest',
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'pycrosGUI=pycrosGUI:main',
        ],
    },
)
