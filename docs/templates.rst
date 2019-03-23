#################
Project Templates
#################

Project templates are example project structures that may include things like
contracts, deploy scripts, and tests all ready to go.  They can help you get
common project structures setup with a simple :code:`sb init -t [template]`
command.

For instnace, you can get an ERC20 project structure setup pretty quick like so:

.. code-block: bash

    sb init -t erc20

***************************
Available Project Templates
***************************

The :code:`bare` template is used by default by the :code:`sb init` command.
For now, there are only options but there may be more to come in the future.

====
bare
====

This is the most rudimentary structure.  It provides you with the expected
directories and some basically empty files. 

This template is the default.

=====
erc20
=====

This is an example ERC20 token contract.  It provides a `MyERC20.sol` contract
source file that you can use as a reference to create your own.  This template
includes example tests and a deployment contract ready to go.
