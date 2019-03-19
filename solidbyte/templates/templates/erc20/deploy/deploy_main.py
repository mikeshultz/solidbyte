"""
main can have the following kwargs:
 - contracts - a dict of all the available contracts
 - deployer_account - the address of the account deploying the contracts
 - web3 - An initialized Web3 object
 - network - The name of the network given in the console arguments
"""


def main(contracts, deployer_account, web3, network):
    assert contracts is not None
    assert deployer_account is not None
    assert web3 is not None
    assert network is not None

    deployer_balance = web3.eth.getBalance(deployer_account)

    if network in ('dev', 'test'):
        # If this is the test network, make sure our deployment account is funded
        if deployer_balance == 0:
            tx = web3.eth.sendTransaction({
                'from': web3.eth.accounts[0],  # The pre-funded account in ganace-cli
                'to': deployer_account,
                'value': int(1e18),
                'gasPrice': int(3e9),
                })
            receipt = web3.eth.waitForTransactionReceipt(tx)
            assert receipt.status == 1
    else:
        # Make sure deployer account has at least 0.5 ether
        assert deployer_balance < int(5e17), "deployer account needs to be funded"

    # Get the sb Contract instance
    token = contracts.get('MyERC20')

    # Deploy (if necessary) and return the web3.eth.Contract instance
    initial_supply = int(1e21)
    web3_contract_instance = token.deployed(initialSupply=initial_supply)

    # If we have an address, deployment was successful
    assert web3_contract_instance.address is not None, "Deploy failed.  No address found"
    assert web3_contract_instance.functions.totalSupply().call() == initial_supply, \
        "totalSupply does not equal initialSupply"

    return True
