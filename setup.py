import os
from setuptools import setup, find_packages

from elvis import __version__ as version

f = open(os.path.join(os.path.dirname(__file__), 'README.md'))
readme = f.read()
f.close()

setup(
    name='python-lvis',
    version=version,
    description='`python-lvis` provides python bindings for ELVIS.',
    long_description=readme,
    author="Thorgate",
    author_email='info@thorgate.eu',
    url='https://thorgate.eu',
    packages=find_packages(),
    install_requires=[
        'requests',
        'django',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
    ],
)
