import atexit
import code
import os
import readline
import rlcompleter
import solidbyte
from ..common.web3 import web3
from ..common.logging import getLogger, parent_logger
from ..deploy import Deployer, get_latest_from_deployed

log = getLogger(__name__)

def get_default_banner(network_id, contracts=[], variables={}):
    return \
        "Solidbyte Console ({})\n" \
        "------------------------------\n" \
        "Network Chain ID: {}\n" \
        "Available deployed contracts: {}\n" \
        "Available locals: {}".format(
            solidbyte.__version__,
            network_id,
            ", ".join(contracts),
            ", ".join(['{}'.format(key) for key, value in variables.items() if key not in contracts])
            )


class SolidbyteConsole(code.InteractiveConsole):
    def __init__(self, _locals=None, filename="<console>", network_id=None,
                 histfile=os.path.expanduser("~/.solidbyte-history")):

        if not _locals:

            d = Deployer(network_id=network_id)
            contracts_meta = d.deployed_contracts
            contracts_compiled = d.source_contracts
            self.contracts = {}
            for meta in contracts_meta:
                if meta['networks'].get(network_id):
                    latest = get_latest_from_deployed(
                        meta['networks'][network_id]['deployedInstances'],
                        meta['networks'][network_id]['deployedHash']
                    )
                    abi = contracts_compiled[meta['name']].abi
                    self.contracts[meta['name']] = web3.eth.contract(abi=abi, address=latest['address'])

            variables = {
                'web3': web3,
            }
            variables.update(self.contracts)

            _locals = variables

        code.InteractiveConsole.__init__(self, _locals, filename)
        self.locals = _locals
        self.histfile = histfile
        self.network_id = network_id
        self.init_history(histfile)

    def interact(self, banner=None, exitmsg="bye!"):
        super(SolidbyteConsole, self).interact(banner \
                                                or get_default_banner(
                                                    self.network_id,
                                                    self.contracts,
                                                    self.locals
                                                ),
                                                exitmsg)

    def init_history(self, histfile):
        readline.parse_and_bind("tab: complete")
        readline.set_completer(rlcompleter.Completer(self.locals).complete)
        try:
            readline.read_history_file(histfile)
        except FileNotFoundError:
            log.warn("History file not found")
        atexit.register(self.save_history, histfile)

    def save_history(self, histfile=None):
        readline.set_history_length(1000)
        readline.write_history_file(histfile)