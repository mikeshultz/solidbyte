from ...accounts import Accounts
from ...common.logging import getLogger

log = getLogger(__name__)


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
        if addr in self.web3.eth.accounts:
            return True
        return self.accounts.account_known(addr)

    def _account_signer(self, addr):
        """ Check if an account is a locally managed 'signer' """
        return self.accounts.account_known(addr)

    def __call__(self, method, params):
        if method == 'eth_sendTransaction':
            new_params = []
            # Go through each parameter set (each call can have multiple)
            for pset in params:
                # Make sure we were given an account
                if pset.get('from'):
                    # Make sure need to sign with the account
                    if self._account_signer(pset['from']):

                        # Sign the TX and add that to the new call's params
                        signed = self.accounts.sign_tx(pset['from'], pset)
                        new_params.append(signed.rawTransaction)

                        # Convert to different JSON-RPC call
                        method = 'eth_sendRawTransaction'
                        params = new_params
                    else:
                        # If the account isn't on the node, either, this is a problem
                        if not self._account_available(pset['from']):
                            # For now, error, but this might-should just fallback to
                            # eth_sendTransaction
                            log.error(("Transaction being sent from unknown account {}. This will "
                                       "probably fail.").format(pset['from']))

        log.debug("method/params: {}/{}".format(method, params))

        # perform the RPC request, getting the response
        response = self.make_request(method, params)
        return response
