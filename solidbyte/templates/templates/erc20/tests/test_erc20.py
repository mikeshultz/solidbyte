
def test_erc20(web3, contracts):
    print("contracts: ", contracts)

    """ We're just going to test to make sure the contracts fixture is being 
        populated with deployed contract instances
    """
    assert contracts.ERC20 is not None
    assert hasattr(contracts.ERC20, 'address')
    assert type(contracts.ERC20.address) == str
    assert len(contracts.ERC20.address) == 42
    assert contracts.ERC20.address[:2] == '0x'

    assert len(web3.eth.accounts) > 0
    admin = web3.eth.accounts[0]

    # Deployed version should have no tokens to start
    assert contracts.ERC20.functions.balanceOf(admin).call() == 0