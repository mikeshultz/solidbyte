# SolidByte Development

If you're looking to hack on SolidByte, you're in the right place.

## Testing

    pytest

## Release

Bump the version with tbump.  This will update the version in the source, create a commit, tag the release as `v[version]` and push it up in the current branch.  All versions will deploy to test.pypi, but alpha/beta will NOT be deployed to prod pypi.

For example, a beta release:

    tbump v0.3.1b1

And a prod release:

    tbump v0.3.1

These will be automagically deployed to PyPi by TravisCI.

## Linting

flake8 is used for linting to PEP8 conventions.  Best to configure it with your
preferred IDE, but you can also run it with the command `python setup.py lint`

## Docstrings

Use [Google's Python doctstring format](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html).
