#!/usr/bin/env python3
# pylint: disable=C0103

from setuptools import setup, find_packages

requirements = open('./requirements.txt').read().splitlines()
long_description = open('./README.md').read()

setup(
  name='lt-pylib',
  version='0.0.1',
  description='Common Python helper functions',
  long_description=long_description,
  long_description_content_type='text/markdown',
  url='https://github.com/lancethomps/lt-pylib',
  project_urls={
      'Bug Reports': 'https://github.com/lancethomps/lt-pylib/issues',
      'Source': 'https://github.com/lancethomps/lt-pylib',
  },
  author='Lance Thompson',
  license='MIT',
  keywords='utils',

  python_requires='>=3',
  extras_require={
      'dev': ['check-manifest'],
      'test': ['coverage'],
  },
  packages=find_packages(exclude=['contrib', 'docs', 'tests']),
  install_requires=requirements,
  classifiers=[],
)
