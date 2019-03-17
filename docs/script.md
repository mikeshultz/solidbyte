# Scripts

## Overview

You can create scrpits that can be run by solidbyte. Solidbyte will provide
these scripts with some useful things, like an instantiated `Web3` object and
`web3.eth.Contract` representations of your smart contracts.

There's no reason it's necessary to create scripts this way, but it's intended
to make things easier.

## Script Implementations

For example scripts, see the [scripts directory of the solidbyte-test-project
repository](https://github.com/mikeshultz/solidbyte-test-project/tree/master/scripts).

The only thing that is required to run your scripts via the `sb script` command
is that you implement the `main()` function.  The following kwargs will be
provided if you include them in your function definition:

- `network` - The name of the network used in the CLI command
- `contracts` - An `AttrDict` of your deployed contracts.
- `web3` - An instantiated Web3 object.
