#################
Project Structure 
#################

The project directory structure pretty straight forward.  Most of this will be
created by :code:`sb init` with a simple template.  This example is what is
created by the :code:`erc20` template:

.. code-block:: text

    project_directory/
        |- build/  # Files created by the compilers, including contract ABIs and their compiled bytecode.
        |- contracts/  # Solidity and/or Vyper contract source files
            |- ERC20.sol
            |- IERC20.sol
            |- SafeMath.sol
        |- deploy/  # Your deployment scripts.
            |- __init__.py
            |- deploy_main.py
        |- tests/  # Contains your pytest tests to test your contracts
            |- __init__.py
            |- test_erc20.py
        |- networks.yml  # Network/node connection configuration
        |- metafile.json  # Project state

For further detailed information, see below.

******
build/
******

This directory should be pretty much hands-off and completely managed by
Solidbyte.  Referencing these files may be useful, but arbitrarily changing
anything may cause unexpected behavior.  There's no real reason to keep this
directory in version control.

**********
contracts/
**********

This directory contains all of your contract source files.  They can be Vyper
or Solidity or a mix of both if you prefer.  The directory structure under this
can be whatever you want.

*******
deploy/
*******

:code:`deploy/` contains your deployment scripts. See: :doc:`deployment`.

******
tests/
******

This contains your pytest scripts. See :doc:`testing`.

************
networks.yml
************

This file contains your connection configuration. See: :doc:`networks`.

*************
metafile.json
*************

This is the file Solidbyte uses to keep track of your project state.  Things
like the default account, and known deployments of your contracts.  Generally,
you probably shouldn't fiddle with this file and it's a great idea to keep this
file in version control if working in a team.  For more information, see
:doc:`metafile`.
