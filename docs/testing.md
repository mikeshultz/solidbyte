# Testing Your Contracts

Testing your contracts with SolidByte is pretty straight forward.  SolidByte
uses [pytest](https://docs.pytest.org/en/latest/) as a test runner and provides
some useful fixtures to help ease testing.

## Fixtures

### `contracts`

The `contracts` fixture is an AttrDict instance with all of your deployed
contracts as `web3.eth.Contract` instances.

### `web3`

This is the initialized instance of Web3 that should already be connected to
whatever network you gave on the CLI.

## Example Test

Here's an example test provided with the `erc20` template:

    def test_erc20(web3, contracts):

        """ We're just going to test to make sure the contracts fixture is being 
            populated with deployed contract instances
        """
        assert 'ERC20' in contracts, "Contract not deployed"
        assert hasattr(contracts.ERC20, 'address')
        assert type(contracts.ERC20.address) == str
        assert len(contracts.ERC20.address) == 42
        assert contracts.ERC20.address[:2] == '0x'

        assert len(web3.eth.accounts) > 0
        admin = web3.eth.accounts[0]

        # Deployed version should have no tokens to start
        assert contracts.ERC20.functions.balanceOf(admin).call() == 0
        assert contracts.ERC20.functions.totalSupply().call() > 0