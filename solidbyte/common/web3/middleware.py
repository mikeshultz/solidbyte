from ...accounts import Accounts

class SolidbyteSignerMiddleware(object):
    """ Middleware that takes eth_sendTransaction calls, signs the tx with 
        Accounts and converts the RPC call to eth_sendRawTransaction.

        Ref
        ---
        https://web3py.readthedocs.io/en/stable/middleware.html
        https://web3py.readthedocs.io/en/stable/internals.html#internals-middlewares
    """
    def __init__(self, make_request, web3):
        self.web3 = web3
        self.make_request = make_request
        self.accounts = Accounts(web3=web3)

    def _account_available(self, addr):
        """ Check if an account is available """
        accounts = self.accounts.get_accounts()
        for a in accounts:
            if a == a.address:
                return True
        return False

    def __call__(self, method, params):
        if method == 'eth_sendTransaction':
            new_params = []
            # Go through each parameter set (each call can have multiple)
            for pset in params:
                # Make sure we can use the account
                if pset.get('from') \
                    and self._account_available(pset['from']) is not None:

                    # Sign the TX and add that to the new call's params
                    signed = self.accounts.sign_tx(pset['from'], pset)
                    new_params.append(signed.rawTransaction)
                else:
                    # For now, error, but this might-should just fallback to eth_sendTransaction
                    log.error("Cannot use account {}".format(pset['from']))
                    raise Exception("Unable to use provided 'from' account")

            # Convert to different JSON-RPC call
            method = 'eth_sendRawTransaction'
            params = new_params

        # perform the RPC request, getting the response
        response = self.make_request(method, params)
        return response
