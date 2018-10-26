""" Solidity compiling functionality """
from os import path, getcwd, listdir
from subprocess import check_call, check_output
from ..common import builddir, source_filename_to_name
from ..common.logging import getLogger, parent_logger

log = getLogger(__name__)

SOLC_PATH = path.normpath(path.join(path.dirname(__file__), '..', 'bin', 'solc'))

class Compiler(object):
    """ Handle compiling of contracts """

    def __init__(self, contract_dir=None):
        self.dir = contract_dir or path.join(getcwd(), 'contracts')
        self.builddir = builddir()

    @property
    def version(self):
        """ Get the version of the copmiler """
        compile_cmd = [
            SOLC_PATH,
            '--version',
        ]
        version_out = check_output(compile_cmd)
        try:
            version_string = version_out.decode('utf8').split('\n')[1]
            return version_string.replace('Version: ', '')
        except:
            return 'err'

    def compile(self, filename):
        """ Compile a single contract with filename """
        log.info("Compiling contract {}".format(filename))

        # Compiler command to run
        compile_cmd = [
            SOLC_PATH,
            '--bin',
            '--overwrite',
            '-o',
            path.join(self.builddir, source_filename_to_name(filename)),
            path.join(self.dir, filename)
        ]
        log.debug("Executing compiler with: {}".format(' '.join(compile_cmd)))

        abi_cmd = [
            SOLC_PATH,
            '--abi',
            '--overwrite',
            '-o',
            path.join(self.builddir, source_filename_to_name(filename)),
            path.join(self.dir, filename)
        ]
        log.debug("Executing compiler with: {}".format(' '.join(abi_cmd)))

        # Do the needful
        compile_retval = check_call(compile_cmd)
        abi_retval = check_call(abi_cmd)
        if compile_retval != 0 or abi_retval != 0:
            raise Exception("Solidity compiler returned non-zero exit code")

    def compile_all(self):
        """ Compile a single contract with filename """

        log.debug("Compiling all contracts with compiler at {}".format(SOLC_PATH))
        log.debug("Contracts directory: {}".format(self.dir))
        log.debug("Build directory: {}".format(self.builddir))

        contract_files = [f for f in listdir(self.dir) if path.isfile(path.join(self.dir, f))]
        log.debug("contract files: {}".format(contract_files))

        for contract in contract_files:
            self.compile(contract)
            