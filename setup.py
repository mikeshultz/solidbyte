import sys
import shutil
import solidbyte
from os import path
from setuptools import Command, setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
from subprocess import check_call, CalledProcessError

pwd = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(pwd, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


class DevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        check_call("/bin/sh scripts/install_solc.sh".split())
        develop.run(self)


# TODO: Revisit, should this install/update solc?
class InstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.do_egg_install(self)


class LintCommand(develop):
    """ Run linting"""
    def run(self):
        try:
            check_call("flake8 --config .flake8".split())
        except CalledProcessError as err:
            if 'non-zero' in str(err):
                print("linting failed with warnings", file=sys.stderr)
                sys.exit(1)


class TestCommand(develop):
    """ Run linting"""
    def run(self):
        try:
            check_call(["pytest"])
        except CalledProcessError as err:
            if 'non-zero' in str(err):
                print("testing failed", file=sys.stderr)
                sys.exit(1)


class GanacheInstallCommand(Command):
    """ Install ganache-cli """
    description = 'Install ganache-cli globally'
    user_options = [
        ('version=', 'v', 'version of ganache to install'),
    ]

    def initialize_options(self):
        self.version = '6.4.1'

    def finalize_options(self):
        pass

    def run(self):
        if shutil.which('ganache-cli'):
            print('Ganache already installed')
            return
        try:
            check_call([shutil.which('npm'), 'install', '-g', 'ganache-cli'])
        except CalledProcessError as err:
            if 'non-zero' in str(err):
                print("extract failed", file=sys.stderr)
                sys.exit(1)


def requirements_to_list(filename):
    return [dep for dep in open(path.join(pwd, filename)).read().split('\n') if (
        dep and not dep.startswith('#')
    )]


setup(
    name='solidbyte',
    version=solidbyte.__version__,
    description='Solidity development tools for creating Ethereum smart contracts',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/mikeshultz/solidbyte',
    author=solidbyte.__author__,
    author_email=solidbyte.__email__,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='solidity ethereum development',
    packages=find_packages(exclude=['docs', 'tests', 'scripts', 'build']),
    install_requires=requirements_to_list('requirements.txt'),
    extras_require={
        'dev': requirements_to_list('requirements.dev.txt'),
        'test': requirements_to_list('requirements.test.txt'),
    },
    entry_points={
        'console_scripts': [
            'sb=solidbyte.cli:main',
        ],
    },
    package_data={
        '': [
            'README.md',
            'LICENSE',
        ],
        'solidbyte': [
            'bin/solc',
            'templates/templates/*/networks.yml',
            'templates/templates/*/contracts/*',
            'templates/templates/*/tests/*',
            'templates/templates/*/deploy/*',
        ],
    },
    cmdclass={
        'develop': DevelopCommand,
        'install': InstallCommand,
        'lint': LintCommand,
        'test': TestCommand,
        'install_ganache': GanacheInstallCommand,
    }
)
