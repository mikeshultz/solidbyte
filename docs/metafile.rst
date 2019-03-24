#############
metafile.json
#############

********
Overview
********

:code:`metafile.json` is a file that holds your project state.  SolidByte may
store things like your default account, or the addresses for your contract
deployments.

If you're working in a team, it may be a good idea to check this in to your VCS.  

**WARNING**: If you lose this file, SolidByte will have no idea if your
contracts are already deployed or not.  This could cause duplicate or broken 
deployments of your contracts. It's also a great idea to at least back it up if
you aren't commiting it to a VCS.

**WARNING**: Editing this file manually, while an option, may cause Solidbyte to
behave unexpectedly.  Edit it at your own risk and make sure to back it up. See
the command: :ref:`metafile-command`

*****************************
Example :code:`metafile.json`
*****************************

Here's an example structure of the `metafile.json` file:

.. code-block:: json

    {
      "contracts": [
        {
          "name": "ExampleContract",
          "networks": {
            "1": {
              "deployedHash": "0xdeadbeef...",
              "deployedInstances": [
                {
                  "hash": "0xdeadbeef...",
                  "date": "2018-10-21 00:00:00T-7",
                  "address": "0xdeadbeef...",
                  "abi": [],
                }
              ]
            }
          }
        }
      ],
      "seenAccounts": [
        "0x208B6deadbeef..."
      ],
      "defaultAccount": "0x208B6deadbeef..."
    }

