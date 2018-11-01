# Deployment Scripts

## Overview

SolidByte aims to make deployment easy.  For the most part, it will keep track
of contract deployments and will know when the source changed and a new version
needs to go up.

However, most deployments are not as simple as just compiling the bytecode and
sending the TX.  That have constructor arguments, or little transactions that
need to be made after deployment is done.  For this, you need to create a 
deployment script.

All scripts are in the `deploy/` directory in your project root, and should be
named starting with `deploy_`.  And SolidByte will only call `main()` within
your deploy scripts.  Any other functions you have will be ignored.

For instance, if you initialized your project with an ERC20 template, you would
get [this deployment script](https://github.com/mikeshultz/solidbyte/blob/master/solidbyte/templates/templates/erc20/deploy/deploy_main.py)
by default.  It's got a little logic for funding your accounts on test network, 
setting the `initialSupply`, and verifying it after deployment.

The important bit is this:

    web3_contract_instance = token.deployed(initialSupply=initial_supply)

The `.deployed()` method on the [`Contract`](https://github.com/mikeshultz/solidbyte/blob/master/solidbyte/deploy/objects.py#L21)
instance is where the magic happens.  This will trigger SolidByte to deploy the
contract again if necessary.  The arguments to this function are the same 
arguments you would provide to your contract's construtor.  It will return a
[web3.py Contract instance](https://web3py.readthedocs.io/en/stable/contracts.html#web3.contract.Contract).

**NOTE**: Using `Contract.deployed()` is not required.  It's there to help.
Feel free not to use it.

SolidByte expects all deploy functions to return True upon success.

### Arguments

SolidByte offers your deploy script's `main()` functions a few optional kwargs.

 - `contracts` - an AttrDict instance of your contract instances stored by name
 - `web3` - An initialized instance of Web3
 - `deployer_account` - The address of the deployer account given on the CLI
 - `network` - The name of the network given on the CLI

Just add any of these kwargs that you want to use to your deploy script's
`main()` function.  For instance: 

    def main(contracts):
        assert isinstance(contracts.ERC20, solidbyte.deploy.objects.Contract)

## Contract Instances

For details on what methods and properties are available for `Contract` instances,
reference [the source for Contract](https://github.com/mikeshultz/solidbyte/blob/master/solidbyte/deploy/objects.py#L21).

More TBD.
