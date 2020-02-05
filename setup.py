#!/usr/bin/env python3
# pylint: disable=C0103

from setuptools import setup, find_packages

requirements = open('./requirements.txt').read().splitlines()
long_description = open('./README.md').read()

setup(
  name='ltpylib',
  version='0.0.3',
  description='Common Python helper functions',
  long_description=long_description,
  long_description_content_type='text/markdown',
  url='https://github.com/lancethomps/ltpylib',
  project_urls={
      'Bug Reports': 'https://github.com/lancethomps/ltpylib/issues',
      'Source': 'https://github.com/lancethomps/ltpylib',
  },
  author='Lance Thompson',
  license='MIT',
  keywords='utils',

  python_requires='>=3',
  extras_require={
      'dev': ['check-manifest'],
      'test': ['coverage'],
  },
  packages=find_packages(exclude=['contrib', 'docs', 'scripts', 'tests']),
  install_requires=requirements,
  classifiers=[],
)
