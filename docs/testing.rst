######################
Testing Your Contracts
######################

Testing your contracts with SolidByte is pretty straight forward.  SolidByte
uses `pytest <https://docs.pytest.org/en/latest/>`_ as a test runner and
provides some useful fixtures to help ease testing.

********
Fixtures
********

=================
:code:`contracts`
=================

The :code:`contracts` fixture is an :code:`AttrDict` instance with all of your
deployed contracts as :class:`web3.contract.Contract` instances.

============
:code:`web3`
============

This is the initialized instance of :class:`web3.Web3` that should already be
connected to whatever network you gave on the CLI.

************
Example Test
************

Here's an example test provided with the :code:`erc20` template:

.. literalinclude:: ../solidbyte/templates/templates/erc20/tests/test_erc20.py
    :pyobject: test_erc20
