
def test_erc20(contracts):
    print("contracts: ", contracts)
    assert contracts.ERC20 is not None
    assert contracts.ERC20 == 'whatever''