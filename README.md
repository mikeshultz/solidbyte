# solidbyte

Solidity development tools for creating Ethereum smart contracts

## Commands 

### init

Create a project using a template or bare.  For instance, creating an ERC20 
project from the template: 

    sb init -t erc20

### compile [In Progress]

Compile the contracts.

    sb compile

### test [In Progress]

Test the contracts using pytest(?)

    sb test

### console 

Start a pythonic console for testing contracts.  Provides web3 and contracts as local variables.

    $ sb console
    2018-10-26 12:23:32,922 [INFO] solidbyte.cli.console - Starting interactive console...
    Solidbyte Console (0.0.1b1)
    ------------------------------
    Available deployed contracts: ERC20
    Available locals: web3
    >>> web3.fromWei(ERC20.functions.balanceOf(web3.eth.accounts[0]).call(), 'ether')
    Decimal('1000')

### deploy [In Progress]

Deploy contracts, upgrading where necessary(?)

### script [Planning]

Execute a python script within the context of soidbyte

### help

Show usage

### install [Planning]

Ethereum package registry? https://www.ethpm.com/

### show

Show details about the deployed contracts

### version

Show versions of solidbyte, the compiler, and associated tools

## metafile.json

This file holds all the metadata for contract deployments.  TBD

Proposed structure: 

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
                            }
                        ]
                    }
                }
            }
        ],
    }