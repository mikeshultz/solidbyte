""" Gas report junk """
from typing import Optional, List, Dict, Tuple
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

    def add_transaction(self, params: List) -> None:

        log.debug("GasReportStorage.add_transaction")

        for tx in params:

            if 'gas' not in tx or 'data' not in tx:
                log.debug("TX: {}".format(tx))
                raise ValueError("Malformed transaction")

            self.transactions.append(GasTransaction(tx['gas'], tx['data']))

    def update_last_transaction_set_hash(self, tx_hash):
        assert len(self.transactions) > 0, "No transactions to update"
        self.transactions[-1].tx_hash = tx_hash

    def update_transaction_gas_used(self, tx_hash, gas_used):
        tx_idx = self._get_tx_idx(tx_hash)
        if tx_idx < 0:
            raise ValueError("Can not update gas used for transaction because it does not exist.")
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
            log.debug("Transaction {} used {} gas".format(self.transactions[idx].tx_hash, receipt.gasUsed))
            self.transactions[idx].gas_used = receipt.gasUsed
            self.total_gas += receipt.gasUsed

    def log_report(self, logger=None) -> None:
        """ Log the report """

        if len(self.report) < 1:
            self._build_report()

        if logger is None:
            logger = log

        for func in self.report.keys():
            lo = min(self.report[func])
            hi = max(self.report[func])
            avg = sum(self.report[func]) / len(self.report[func])
            if lo == hi:
                logger.info("{}: {}".format(func, lo))
            else:
                logger.info("{}: Low: {}  High: {}  Avg: {}".format(func, lo, hi, avg))

        logger.info("Total Transactions: {}".format(len(self.transactions)))
        logger.info("Total Gas: {}".format(self.total_gas))
        logger.info("Average Gas per Transaction: {}".format(
            self.total_gas / len(self.transactions)
        ))

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
                gas_report_storage.add_transaction(params)
            elif method == 'eth_sendRawTransaction':
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
