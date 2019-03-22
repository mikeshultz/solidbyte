""" Solidity compiling functionality """
import json
import vyper
from subprocess import Popen, PIPE, STDOUT
from pathlib import Path
from typing import Set
from vyper.signatures.interface import extract_file_interface_imports
from .vyper import is_vyper_interface, vyper_import_to_file_paths
from ..common.utils import (
    builddir,
    get_filename_and_ext,
    supported_extension,
    find_vyper,
    to_path_or_cwd,
)
from ..common.exceptions import CompileError
from ..common.logging import getLogger

log = getLogger(__name__)

SOLC_PATH = str(Path(__file__).parent.joinpath('..', 'bin', 'solc').resolve())
VYPER_PATH = find_vyper()


def get_all_source_files(contracts_dir: Path) -> Set[Path]:
    """ Return a Path for every contract source file in the provided directory and any sub-
    directories.

    :param contracts_dir: The Path of the directory to start at.
    :returns: List of Paths to every source file in the directory.
    """
    source_files: Set[Path] = set()
    for node in contracts_dir.iterdir():
        if node.is_dir():
            source_files.update(get_all_source_files(node))
        elif node.is_file():
            if supported_extension(node):
                source_files.add(node)
        else:
            log.error("{} is not a known fs type.".format(str(node)))
            raise Exception("Path is an unknown.")
    return source_files


class Compiler(object):
    """ Handle compiling of contracts """

    def __init__(self, project_dir=None):
        self.dir = to_path_or_cwd(project_dir).joinpath('contracts')
        self.builddir = builddir(project_dir)

    @property
    def solc_version(self):
        """ Get the version of the solidity copmiler """
        compile_cmd = [
            SOLC_PATH,
            '--version',
        ]
        p = Popen(compile_cmd, stdout=PIPE)
        version_out = p.stdout.read()
        p.wait()
        try:
            version_string = version_out.decode('utf8').split('\n')[1]
            return version_string.replace('Version: ', '')
        except Exception:
            return 'err'

    @property
    def vyper_version(self):
        """ Get the version of the vyper copmiler """
        return vyper.__version__

    @property
    def version(self):
        return [self.solc_version, self.vyper_version]

    def compile(self, filename):
        """ Compile a single contract with filename """
        log.info("Compiling contract {}".format(filename))

        # Get our ouput FS stuff ready
        source_file = Path(self.dir, filename)
        name, ext = get_filename_and_ext(filename)
        contract_outdir = Path(self.builddir, name)
        contract_outdir.mkdir(mode=0o755, exist_ok=True, parents=True)
        bin_outfile = contract_outdir.joinpath('{}.bin'.format(name))
        abi_outfile = contract_outdir.joinpath('{}.abi'.format(name))

        if ext == 'sol':

            # Compiler command to run
            compile_cmd = [
                SOLC_PATH,
                '--bin',
                '--optimize',
                '--overwrite',
                '--allow-paths',
                str(self.dir),
                '-o',
                str(bin_outfile.parent),
                str(source_file)
            ]
            log.debug("Executing compiler with: {}".format(' '.join(compile_cmd)))

            abi_cmd = [
                SOLC_PATH,
                '--abi',
                '--overwrite',
                '--allow-paths',
                str(self.dir),
                '-o',
                str(abi_outfile.parent),
                str(source_file)
            ]
            log.debug("Executing compiler with: {}".format(' '.join(abi_cmd)))

            # Do the needful
            p_bin = Popen(compile_cmd, stdout=PIPE, stderr=STDOUT)
            p_abi = Popen(abi_cmd, stdout=PIPE, stderr=STDOUT)

            # Twiddle our thumbs
            p_bin.wait()
            p_abi.wait()

            # Check the output
            p_bin_out = p_bin.stdout.read()
            p_abi_out = p_abi.stdout.read()
            if (
                b'Compiler run successful' not in p_bin_out
                and b'Compiler run successful' not in p_abi_out
                    ):
                log.error("Compiler shows an error:")
                raise CompileError("solc did not indicate success.")

            # Check the return codes
            compile_retval = p_bin.returncode
            abi_retval = p_abi.returncode
            if compile_retval != 0 or abi_retval != 0:
                raise CompileError("Solidity compiler returned non-zero exit code")

            if bin_outfile.stat().st_size == 0:
                """ So far this has been seen with contracts that inherit  an interface.  Perhaps
                missing some implementations or conflicts, but solc doesn't complain.  Not sure why
                solc doesn't throw an error, but here we are.
                """
                log.warning("Zero length bytecode output from compiler. This is fine for "
                            "interfaces but may indicate a silent error with {}.".format(name))
                # raise CompileError("Zero length bytecode output from compiler. Check your "
                #                    "interface implementations.")

        elif ext == 'vy':

            source_text = ''

            with source_file.open() as _file:
                source_text = _file.read()

            if not source_text:
                # TODO: Do we want to die in a fire here?
                log.warning("Source file for {} appears to be empty!".format(name))
                return

            if is_vyper_interface(source_text):
                log.warning("{} appears to be a vyper interface.  Skipping.".format(name))
                return

            # Read in the source for the interface(s)
            interface_imports = extract_file_interface_imports(source_text)
            interface_codes = dict()

            for interface_name, interface_path in interface_imports.items():
                interface_filepath = vyper_import_to_file_paths(self.dir, interface_path)
                with interface_filepath.open() as _file:
                    interface_codes[interface_name] = {
                        'type': 'vyper',
                        'code': _file.read()
                    }

            compiler_out = vyper.compile_code(
                source_text,
                ['bytecode', 'abi'],
                interface_codes=interface_codes,
            )

            if not compiler_out.get('bytecode') and not compiler_out.get('abi'):
                log.error("Nothing returned by vyper compiler for {}".format(name))
                return

            if not compiler_out.get('bytecode'):
                log.warning("No bytecode returned by vyper compiler for contract {}".format(name))
            else:

                # Create the output file and open for writing of bytecode
                with bin_outfile.open(mode='w') as out:
                    out.write(compiler_out['bytecode'])

            # ABI
            if not compiler_out.get('abi'):
                log.warning("No ABI returned by vyper compiler for contract {}".format(name))
            else:

                # Create the output file and open for writing of bytecode
                with abi_outfile.open(mode='w') as out:
                    out.write(json.dumps(compiler_out['abi']))

        else:
            raise CompileError("Unsupported source file type")

    def compile_all(self):
        """ Compile a single contract with filename """

        log.debug("Compiling all contracts with compiler at {}".format(SOLC_PATH))
        log.debug("Contracts directory: {}".format(self.dir))
        log.debug("Build directory: {}".format(self.builddir))

        source_dir = Path(self.dir)
        contract_files = get_all_source_files(source_dir)

        log.debug("contract files: {}".format(contract_files))

        for contract in contract_files:
            self.compile(contract)
