import solidbyte
from os import path
from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
from subprocess import check_call

pwd = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(pwd, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


class DevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        check_call("/bin/sh scripts/install_solc.sh".split())
        develop.run(self)


class InstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)


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
    install_requires=open(path.join(pwd, 'requirements.txt')).read().split(),
    extras_require={
        'dev': open(path.join(pwd, 'requirements.dev.txt')).read().split(),
        'test': open(path.join(pwd, 'requirements.test.txt')).read().split(),
    },
    entry_points={  # Optional
        'console_scripts': [
            'sb=solidbyte.cli:main',
        ],
    },
    package_data={
        'solidbyte': [
            'bin/solc',
            'templates/templates/*/networks.yml',
            'templates/templates/*/contracts/*',
            'templates/templates/*/tests/*',
            'templates/templates/*/deploy/*',
        ]
    },
    cmdclass={
        'develop': DevelopCommand,
        'install': InstallCommand,
    }
)