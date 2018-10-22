# solidbyte

Solidity development tools for creating Ethereum smart contracts

## Commands 

### init [Planning]

Create a project template or create meta files.

### compile [Planning]

Compile the contracts.

### test [Planning]

Test the contracts using pytest(?)

### console [Planning]

Start a pythonic console for testing contracts.  Provide web3 globally

### deploy [Planning]

Deploy contracts, upgrading where necessary(?)

### script [Planning]

Execute a python script within the context of soidbyte

### help [Planning]

Show usage

### install [Planning]

Ethereum package registry? https://www.ethpm.com/

### show [Planning]

Show details about the deployed contracts

### version [Planning]

Show versions of solidbyte, the compiler, and associated tools

## metafile.json

This file holds all the metadata for contract deployments.  TBD

Proposed structure: 

    {
        "contracts": [
            {
                "name": "ExampleContract",
                "deployedHash": "0xdeadbeef...",
                "deployedInstances": [
                    {
                        "hash": "0xdeadbeef...",
                        "date": "2018-10-21 00:00:00T-7",
                        "address": "0xdeadbeef...",
                    }
                ]
            }
        ],
    }