# Commands 

## `init`

Create a project using a template or bare.  For instance, creating an ERC20 
project from the template: 

    sb init -t erc20

## `compile`

Compile the contracts.

    sb compile

## `test`

Test the contracts using pytest(?)

    sb test

## `console` 

Start a pythonic console for testing contracts.  Provides web3 and contracts as local variables.

    $ sb console dev
    2018-10-28 17:42:38,022 [INFO] solidbyte.cli.console - Starting interactive console...
    Solidbyte Console (0.0.1b1)
    ------------------------------
    Network Chain ID: 1540751678531
    Available deployed contracts: MyToken
    Available locals: web3
    >>>

## `deploy`

Deploy contracts using the user-written deploy scripts.  For more details, see
the [deployment documentation](deployment.md).

## `help`

Show usage

## `show`

Show details about the deployed contracts

## `version`

Show versions of solidbyte, the compiler, and associated tools

## `script` [Planning]

Execute a python script within the context of soidbyte

## `install` [Planning]

Ethereum package registry? https://www.ethpm.com/

## `metafile`

Commands to backup and cleanup the metafile.

### `metafile cleanup`

Cleanup and compact `metafile.json` by removing deployed contract instances for test networks.

### `metafile backup`

Make a copy of `metafile.json` to the given location and verify.

## `sigs`

Show all event and function signatures for the compiled contracts.
