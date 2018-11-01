# metafile.json

`metafile.json` is a file that holds your project state.  SolidByte may store
things like your default account, or the addresses for your contract
deployments.

If you're working in a team, it may be a good idea to check this in.  It's also
a great idea to back it up.  **If you lose this file, SolidByte will have no
idea if your contracts are already deployed or not**.  So, don't lose it.

**WARNING**: Editing this file manually, while an option, may cause SolidByte to
behave unexpectedly.  Edit it at your own risk.

## Example

Here's an example structure of the `metafile.json` file:

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

