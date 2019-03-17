
def test_erc20(web3, contracts):
    print("contracts: ", contracts)

    """ We're just going to test to make sure the contracts fixture is being
        populated with deployed contract instances
    """
    assert 'MyERC20' in contracts, "Contract not deployed"
    assert hasattr(contracts.MyERC20, 'address')
    assert type(contracts.MyERC20.address) == str
    assert len(contracts.MyERC20.address) == 42
    assert contracts.MyERC20.address[:2] == '0x'

    assert len(web3.eth.accounts) > 0
    admin = web3.eth.accounts[0]

    # Deployed version should have no tokens to start
    assert contracts.MyERC20.functions.balanceOf(admin).call() == 0
    assert contracts.MyERC20.functions.totalSupply().call() > 0
