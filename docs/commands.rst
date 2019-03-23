########
Commands 
########

************
:code:`init`
************

Create a project using a template or bare.  For instance, creating an ERC20 
project from the template: 

.. code-block:: bash

    sb init -t erc20

***************
:code:`compile`
***************

Compile the contracts.

.. code-block:: bash

    sb compile

************
:code:`test`
************

Test the contracts using pytest(?)

.. code-block:: bash

    sb test

***************
:code:`console`
***************

Start a pythonic console for testing contracts.  Provides web3 and contracts as
local variables.

.. code-block:: bash

    $ sb console dev
    2018-10-28 17:42:38,022 [INFO] solidbyte.cli.console - Starting interactive console...
    Solidbyte Console (0.0.1b1)
    ------------------------------
    Network Chain ID: 1540751678531
    Available deployed contracts: MyToken
    Available locals: web3
    >>>

**************
:code:`deploy`
**************

Deploy contracts using the user-written deploy scripts.  For more details, see
:doc:`deployment`.

************
:code:`help`
************

Show usage

************
:code:`show`
************

Show details about the deployed contracts

***************
:code:`version`
***************

Show versions of solidbyte, the compiler, and associated tools

**************
:code:`script`
**************

Execute a python script within the context of soidbyte

***************************
:code:`install` [Prototype]
***************************

`Ethereum package manager`_ support.  Coming soon...

.. _Ethereum package manager: https://www.ethpm.com/

.. _metafile-command:

****************
:code:`metafile`
****************

Commands to backup and cleanup the metafile.

========================
:code:`metafile cleanup`
========================

Cleanup and compact :code:`metafile.json` by removing deployed contract
instances for test networks.

=======================
:code:`metafile backup`
=======================

Make a copy of :code:`metafile.json` to the given location and verify.

************
:code:`sigs`
************

Show all event and function signatures for the compiled contracts.
