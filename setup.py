import os
from setuptools import find_packages, setup


here = os.path.dirname(os.path.abspath(__file__))
long_description = open(os.path.join(here, 'README.md')).read()

setup(name='starlog',
      version='1.1.0a1',
      description='Advanced logging features.',
      author='Michael Peick',
      author_email='michael.peick+starlog@gmail.com',
      url='https://gitlab.com/peick/starlog',
      license='gpl-3.0',
      long_description=long_description,
      long_description_content_type='text/markdown',
      keywords=['logging', 'log handler', 'status logging',
                'multiprocessing', 'zmq'],
      packages=find_packages(),
      install_requires=[
          'six',
      ],
      extras_require={
          'zmq': [
              'pyzmq',
          ],
      },
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'Topic :: System :: Logging',
      ]
      )
