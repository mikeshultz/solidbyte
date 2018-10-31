from ...accounts import Accounts

class SolidbyteSignerMiddleware(object):
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
        # do pre-processing here
        print("###############################################################")
        print("method/params: {}/{}".format(method, params))
        print("###############################################################")

        if method == 'eth_sendTransaction':
            print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& eth_sendTransaction")
            new_params = []
            for pset in params:
                if pset.get('from') \
                    and self._account_available(pset['from']) is not None:

                    signed = self.accounts.sign_tx(pset['from'], pset)
                    new_params.append(signed.rawTransaction)
                    print("signed", signed)
                else:
                    log.error("Cannot use account {}".format(pset['from']))
                    raise Exception("Unable to use provided 'from' account")

            method = 'eth_sendRawTransaction'
            params = new_params

        # perform the RPC request, getting the response
        response = self.make_request(method, params)

        # do post-processing here

        # finally return the response
        return response
