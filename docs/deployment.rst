##################
Deployment Scripts
##################

********
Overview
********

Solidbyte aims to make deployment easy.  For the most part, it will keep track
of contract deployments and will know when the source changed and a new version
needs to go up.

However, most deployments are not as simple as just compiling the bytecode and
sending the TX.  That have constructor arguments, or little transactions that
need to be made after deployment is done.  For this, you need to create a 
deployment script.

All scripts are in the :code:`deploy/` directory in your project root, and
should be named starting with :code:`deploy_`.  And Solidbyte will only call
:code:`main()` within your deploy scripts.  Any other functions you have will
be ignored.

For instance, if you initialized your project with an ERC20 template, you would
get the following deployment script by default.  It's got a little logic for
funding your accounts on test network,  setting the :code:`initialSupply`,
and verifying it after deployment.

.. literalinclude:: ../solidbyte/templates/templates/erc20/deploy/deploy_main.py
    :pyobject: main

The important bit is this:

.. literalinclude:: ../solidbyte/templates/templates/erc20/deploy/deploy_main.py
    :pyobject: main
    :lines: 29

The :code:`.deployed()` method on the :class:`solidbyte.deploy.objects.Contract`
instance is where the magic happens.  This will trigger Solidbyte to deploy the
contract if necessary.  The arguments to this function are the same arguments
you would provide to your contract's construtor.  It will return a
:class:`web3.contract.Contract` instance.

**NOTE**: Using :code:`Contract.deployed()` is not required.  It's there to
help. Feel free not to use it.

Solidbyte expects all deploy functions to return True upon success.

=================
Linking Libraries
=================

Linking libraries can be done simply, like so:

.. code-block:: python

    w3Instance = myContract.deployed(links={
            'MyLibrary': '0x48292eafdc...',
        })

The Solidbyte linker will automatically splice these addresss into your solc compiled bytecode. A
more real-world example would be deploying both at the same time:

.. code-block:: python

    myLibrary = contracts.get('MyLibrary')
    myContract = contracts.get('MyContract')

    library = myLibrary.deployed()
    inst = myContract.deployed(links={
            'MyLibrary': library.address
        })

=========
Arguments
=========

Solidbyte offers your deploy script's `main()` functions a few optional kwargs.

 - :code:`contracts` - an AttrDict instance of your contract instances stored by name
 - :code:`web3` - An initialized instance of Web3
 - :code:`deployer_account` - The address of the deployer account given on the CLI
 - :code:`network` - The name of the network given on the CLI

Just add any of these kwargs that you want to use to your deploy script's
:code:`main()` function.  For instance: 

.. code-block:: python

    def main(contracts):
        assert isinstance(contracts.ERC20, solidbyte.deploy.objects.Contract)

******************
Contract Instances
******************

For details on what methods and properties are available for your
:code:`Contract`, see: :class:`solidbyte.deploy.objects.Contract`.

More TBD.
