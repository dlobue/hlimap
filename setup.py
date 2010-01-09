from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='hlimap',
      version=version,
      description="High-level IMAP abstraction library for use with imaplibii",
      long_description="""\
long_desc _morelater_""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='imap library',
      author='Helder Guerreiro',
      author_email='hguerreiro@gmail.com',
      url='http://code.google.com/p/webpymail/',
      license='GNU General Public License v3',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
