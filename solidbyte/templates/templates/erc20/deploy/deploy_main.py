"""
main can have the following kwargs: 
 - contracts - a dict of all the available contracts
"""

def main(contracts):
    # Get the sb Contract instance
    token = contracts.get('ERC20')

    # Deploy (if necessary) and return the web3.eth.Contract instance
    web3_contract_instance = token.deployed(initialSupply=int(1e21))

    # If we have an address, deployment was successful
    return web3_contract_instance.address is not None \
        and web3_contract_instance.functions.totalSupply().call() == 1e21