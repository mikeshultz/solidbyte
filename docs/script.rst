#######
Scripts
#######

********
Overview
********

You can create scrpits that can be run by solidbyte. Solidbyte will provide
these scripts with some useful things, like an instantiated :class:`web3.Web3`
object and :class:`web3.contract.Contract` representations of your smart
contracts.

There's no reason it's necessary to create scripts this way, but it's intended
to make things easier.

=======================
Example Implementations
=======================

For example scripts, see the `scripts directory of the solidbyte-test-project`_
repository.

.. _`scripts directory of the solidbyte-test-project`: https://github.com/mikeshultz/solidbyte-test-project/tree/master/scripts

************
Requirements
************

The following **must** be implemented in your script for Solidbyte to be able
to run it.

==============
:code:`main()`
==============

A :code:`main()` function is expected by Solidbyte when running the 
:code:`sb script` command.  The following kwargs will be provided if you
include them in your function definition:

- :code:`network` - The name of the network used in the CLI command
- :code:`contracts` - An `AttrDict` of your deployed contracts.
- :code:`web3` - An instantiated :class:`web3.Web3` object.

A return value is not required, but if :code:`main()` returns :code:`False`,
Solidbyte will consider that an error state.
