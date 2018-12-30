# solidbyte
[![Build Status](https://travis-ci.org/mikeshultz/solidbyte.svg?branch=master)](https://travis-ci.org/mikeshultz/solidbyte) [![Coverage Status](https://coveralls.io/repos/github/mikeshultz/solidbyte/badge.svg?branch=master)](https://coveralls.io/github/mikeshultz/solidbyte?branch=master)

Development tools for creating Ethereum smart contracts

**NOTE**: Solidbyte has **only been tested on Linux**.  If you use another OS, please consider testing and [submit an issue](https://github.com/mikeshultz/solidbyte/issues/new) for any bugs you find.

## Contents

 - [Documentation](https://github.com/mikeshultz/solidbyte/blob/master/docs/index.md)
 - [Command Reference](https://github.com/mikeshultz/solidbyte/blob/master/docs/commands.md)
 - [metafile.json](https://github.com/mikeshultz/solidbyte/blob/master/docs/metafile.md)
 - [networks.yml](https://github.com/mikeshultz/solidbyte/blob/master/docs/networks.md)
 - [SolidByte Development](https://github.com/mikeshultz/solidbyte/blob/master/docs/development.md)

## Quickstart

### 1) Install Solidbyte

Solidbyte requires some system-level libraries to be installed first.  Make sure openssl/libssl and libffi headers are installed before proceeding.  For more information, see the longer [installation docs](https://github.com/mikeshultz/solidbyte/blob/master/docs/install.md).

First, install solidbyte.  The easiest way to do that is from [PyPi](https://pypi.org)
with `pip`.

    pip install solidbyte

### 2) Setup your project

To get your project going, create a directory for your project and change to it.
Most `sb` commands need to be run from the root of your project directory.

    mkdir myproject && cd myproject
    sb init

Now, all you should have a bare project structure created.  You could also
`init` with [an available template](https://github.com/mikeshultz/solidbyte/blob/master/docs/templates.md),
but for the purposes of this doc, we're just going to create a bare structure.

Your contracts should be in the `contracts` directory.  Your Solidity or Vyper
contracts can be in any directory under it.

The `deploy` directory will hold your [deployment scripts](https://github.com/mikeshultz/solidbyte/blob/master/docs/deployment.md).

And `tests` will contain your [contract unit tests](https://github.com/mikeshultz/solidbyte/blob/master/docs/testing.md).

The `build` directory probably doesn't exist yet.  This will be created by
solidbyte when necessary.
