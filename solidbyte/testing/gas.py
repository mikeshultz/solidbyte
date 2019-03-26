""" Gas report junk """
from typing import Optional, List, Dict
from ..common.web3 import func_sig_from_input, normalize_hexstring
from ..common.logging import getLogger

log = getLogger(__name__)


class GasTransaction(object):
    def __init__(self, gas_limit, data):
        self.gas_limit = gas_limit
        self.data = data
        self.tx_hash = None
        self.gas_used = None
        self.func_sig: Optional[str] = func_sig_from_input(data)


class GasReportStorage(object):
    """ Simple transaction gas storage """

    def __init__(self):
        self.transactions: List[GasTransaction] = list()
        self.total_gas: int = 0
        self.report: Dict[str, List[int]] = dict()
        self.skip_last = False

    def add_transaction(self, params: List) -> None:

        log.debug("GasReportStorage.add_transaction")

        for tx in params:

            if 'gas' not in tx:
                log.debug("TX: {}".format(tx))
                raise ValueError("Malformed transaction")

            # We only want to track transactions with contract calls
            if 'data' not in tx:
                self.skip_last = True
                continue

            self.transactions.append(GasTransaction(tx['gas'], tx['data']))

    def update_last_transaction_set_hash(self, tx_hash):
        if len(self.transactions) < 1 or self.skip_last:
            self.skip_last = False
            return
        self.transactions[-1].tx_hash = tx_hash

    def update_transaction_gas_used(self, tx_hash, gas_used):
        tx_idx = self._get_tx_idx(tx_hash)
        if tx_idx < 0:
            log.debug("Can not update gas used for transaction because it does not exist.")
            return
        self.transactions[tx_idx].gas_used = gas_used
        self.total_gas += gas_used

    def update_gas_used_from_chain(self, web3):
        """ Update all the transactions with gasUsed after the fact """

        if not web3:
            raise Exception("Brother, I need a web3 instance.")

        log.debug("Updating transactions with gasUsed from receipts...")

        for idx in range(0, len(self.transactions)):
            receipt = web3.eth.getTransactionReceipt(self.transactions[idx].tx_hash)
            if not receipt:
                raise ValueError("Unable to get receipt for tx: {}".format(
                    self.transactions[idx].tx_hash
                ))
            if receipt.status == 0:
                log.warning("Gas reporter found a failed transaction")
                continue
            log.debug("Transaction {} used {} gas".format(self.transactions[idx].tx_hash,
                                                          receipt.gasUsed))
            self.transactions[idx].gas_used = receipt.gasUsed
            self.total_gas += receipt.gasUsed

    def get_report(self, force=False):

        if len(self.report) < 1 or force:
            self._build_report()

        return self.report

    def _build_report(self) -> None:
        self.report = {}

        log.debug("Building report...")

        for tx in self.transactions:
            if tx.func_sig:
                if tx.func_sig not in self.report:
                    self.report[tx.func_sig] = [tx.gas_used]
                else:
                    self.report[tx.func_sig].append(tx.gas_used)
            else:
                log.warn("No function signature")

        log.debug("Report finished.")

    def _get_tx_idx(self, tx_hash) -> int:
        """ Get the index for a transaction with tx_hash """
        for idx in range(0, len(self.transactions)):
            if self.transactions[idx].tx_hash == tx_hash:
                return idx
        return -1


def construct_gas_report_middleware(gas_report_storage):
    """ Create a middleware for web3.py """

    def gas_report_middleware(make_request, web3):
        """ web3.py middleware for building a gas report """

        def middleware(method, params):

            if method == 'eth_sendTransaction':
                log.debug("gas_report_middleware eth_sendTransaction: {}".format(params))
                gas_report_storage.add_transaction(params)
            elif method == 'eth_sendRawTransaction':
                log.debug("gas_report_middleware eth_sendRawTransaction: {}".format(params))
                log.warning("Raw transactions will be excluded from the gas report.")

            response = make_request(method, params)

            if method == 'eth_sendTransaction':
                if 'result' in response:
                    tx_hash = normalize_hexstring(response['result'])
                    log.debug("tx_hash: {}".format(tx_hash))
                    gas_report_storage.update_last_transaction_set_hash(tx_hash)
                else:
                    log.warning("Malformed response: {}".format(response))

            return response

        return middleware

    return gas_report_middleware
