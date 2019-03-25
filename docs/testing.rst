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

The :code:`contracts` fixture is an :class:`attrdict.AttrDict` instance with all of your
deployed contracts as :class:`web3.contract.Contract` instances.

============
:code:`web3`
============

This is the initialized instance of :class:`web3.Web3` that should already be
connected to whatever network you gave on the CLI.

======================
:code:`local_accounts`
======================

:code:`list` of addresses of the known local accounts.

=================
:code:`has_event`
=================

Function to check if a receipt contains an event.

.. autofunction:: solidbyte.testing.fixtures.has_event

=================
:code:`get_event`
=================

Function to pull the event data from a receipt.

.. autofunction:: solidbyte.testing.fixtures.get_event

************
Example Test
************

Here's an example test provided with the :code:`erc20` template:

.. literalinclude:: ../solidbyte/templates/templates/erc20/tests/test_erc20.py
    :pyobject: test_erc20
