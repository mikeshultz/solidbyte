# solidbyte
[![Build Status](https://travis-ci.org/mikeshultz/solidbyte.svg?branch=master)](https://travis-ci.org/mikeshultz/solidbyte) [![Coverage Status](https://coveralls.io/repos/github/mikeshultz/solidbyte/badge.svg?branch=master)](https://coveralls.io/github/mikeshultz/solidbyte?branch=master)

Development tools for creating Ethereum smart contracts

### What makes Solidbyte different?

- **Local accounts** - Solidbyte can use the local accounts stored as Ethereum secretstore files located at `~/.ethereum/keystore`.  You do not need to trust the node you are using to handle your private keys and risk opening your account with `personal.unlock`.
- **Python!** - Deploy scripts and tests are written using Python.
- **EthPM support** - Well, it's in progress and not usable yet, but... it probably will be at some point.
- **Vyper and Solidity support** -  Contracts written in either language can co-exist side by side with eachother in your project.
- **Interactive python console** - Solidbyte provides a console with an insantiated Web3 object and your deployed contract instances.  Have I mentioned Python yet?
- **Projcet templates** - You can initialize a project template with a single command that includes example deploy scripts, tests, and contracts.  Right now only 'bare' and 'erc20' templates are available, but I hope to add more.
- **Contract testing with pytest** - Pytest is used for contract testing with some provided fixtures.  Something something Python.
- **[eth_tester](https://github.com/ethereum/eth-tester/) support for testing** - It's super fast and really useful for first-pass testing.

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
