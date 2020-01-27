from setuptools import setup, find_packages
from codecs import open
from os import path, environ
import sys

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'docs/description.rst'), encoding='utf-8') as f:
        long_description = f.read()

with open(path.join(here, 'VERSION'), mode='r', encoding='utf-8') as version_file:
        version = version_file.read().strip()

setup(
    name='pyeapi',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=version,

    description='Python Client for eAPI',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/arista-eosplus/pyeapi',

    # Author details
    author='Arista EOS+ CS',
    author_email='eosplus-dev@arista.com',

    # Choose your license
    license='BSD-3',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        'Intended Audience :: System Administrators',
        'Topic :: System :: Networking',

        'License :: OSI Approved :: BSD License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
    ],

    keywords='networking arista eos eapi',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),

    # List run-time dependencies here.  These will be installed by pip when your
    # project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['netaddr'],

    # List additional dependencies here (e.g. development dependencies).
    # You can install these using the following syntax, for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'dev': ['check-manifest', 'pep8', 'pyflakes', 'twine'],
        'test': ['coverage', 'mock'],
    },
)

def install():
    if "install" in sys.argv:
        return True
    else:
        return False

# Use the following to dynamically build pyeapi module documentation
if install() and environ.get('READTHEDOCS'):
    print('This method is only called by READTHEDOCS.')
    from subprocess import Popen
    proc = Popen(['make', 'modules'], cwd='docs/')
    (_, err) = proc.communicate()
    return_code = proc.wait()

    if return_code or err:
        raise ('Failed to make modules.(%s:%s)' % (return_code, err))
