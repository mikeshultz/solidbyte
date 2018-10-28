# solidbyte

Solidity development tools for creating Ethereum smart contracts

## Contents

 - [Documentation](docs/index.md)
 - [Command Reference](docs/commands.md)
 - [metafile.json](docs/metafile.md)
 - [networks.yml](docs/networks.md)

## Quickstart

### 1) Install Solidbyte

First, install solidbyte.  The easiest way to do that is from [PyPi](https://pypi.org)
with `pip`.

    pip install solidbyte

### 2) Setup your project

To get your project going, create a directory for your project and change to it.
Most `sb` commands need to be run from the root of your project directory.

    mkdir myproject && cd myproject
    sb init

Now, all you should have a bare project structure created.  You could also
`init` with [an available template](docs/templates.md), but for the purposes of this
doc, we're just going to create a bare structure.

Your contracts should be in the `contracts` directory.  Your Solidity or Vyper
contracts can be in any directory under it.

The `deploy` directory will hold your [deployment scripts](docs/deployment.md).

And `tests` will contain your [contract unit tests](docs/testing.md).

The `build` directory probably doesn't exist yet.  This will be created by
solidbyte when necessary.
