from setuptools import setup, find_packages
from codecs import open
from os import path
import sys
from setuptools.command.test import test as TestCommand

__version__ = '0.2.0'

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# get the dependencies and installs
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
dependency_links = [x.strip().replace('git+', '') for x in all_reqs if 'git+' not in x]

# 
class Tox(TestCommand):
    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]
    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = None
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import tox
        import shlex
        args = self.tox_args
        if args:
            args = shlex.split(self.tox_args)
        errno = tox.cmdline(args=args)
        sys.exit(errno)

setup(
    name='messages2json',
    version=__version__,
    description='A program that can be used to convert messages stored in various mailbox formats into JSON format.',
    long_description=long_description,
    url='https://github.com/jmjj/messages2json',
    download_url='https://github.com/jmjj/messages2json/tarball/' + __version__,
    license='MIT',
    classifiers=[
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Developers',
      'Topic :: Communications :: Email',
      'Programming Language :: Python :: 3',
    ],
    keywords='',
    packages=find_packages(exclude=['docs', 'tests*']),
    include_package_data=True,
    author='Jari Juopperi',
    install_requires=install_requires,
    tests_require = ['tox','nose'],
    cmdclass = {'test': Tox},
    entry_points = {
        'console_scripts' :  ['messages2json=messages2json.command_line:main'],    
    },
    dependency_links=dependency_links,
    author_email='jmjj@juopperi.org'
)
