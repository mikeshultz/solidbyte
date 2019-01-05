""" Solidity compiling functionality """
from subprocess import Popen, PIPE
from pathlib import Path
from ..common import (
    builddir,
    get_filename_and_ext,
    supported_extension,
    find_vyper,
    to_path_or_cwd,
)
from ..common.exceptions import CompileError
from ..common.logging import getLogger

log = getLogger(__name__)

SOLC_PATH = str(Path(__file__).parent.joinpath('..', 'bin', 'solc'))
VYPER_PATH = find_vyper()


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
        compile_cmd = [
            VYPER_PATH,
            '--version',
        ]
        p = Popen(compile_cmd, stdout=PIPE)
        version_out = p.stdout.read().decode('utf-8').strip('\n')
        p.wait()
        return version_out

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
                '-o',
                str(bin_outfile.parent),
                str(source_file)
            ]
            log.debug("Executing compiler with: {}".format(' '.join(compile_cmd)))

            abi_cmd = [
                SOLC_PATH,
                '--abi',
                '--overwrite',
                '-o',
                str(abi_outfile.parent),
                str(source_file)
            ]
            log.debug("Executing compiler with: {}".format(' '.join(abi_cmd)))

            # Do the needful
            p_bin = Popen(compile_cmd)
            p_abi = Popen(abi_cmd)

            # Twiddle our thumbs
            p_bin.wait()
            p_abi.wait()

            # Check the return codes
            compile_retval = p_bin.returncode
            abi_retval = p_abi.returncode
            if compile_retval != 0 or abi_retval != 0:
                raise CompileError("Solidity compiler returned non-zero exit code")

        elif ext == 'vy':

            # Create the output file and open for writing of bytecode
            with bin_outfile.open(mode='wb') as out:
                compile_cmd = [
                    VYPER_PATH,
                    '-f',
                    'bytecode',
                    str(source_file)
                ]
                log.debug("Executing compiler with: {}".format(' '.join(compile_cmd)))

                # Execute and write output to outfile
                p = Popen(compile_cmd, bufsize=1, stdout=PIPE)
                for ln in p.stdout:
                    out.write(ln)
                p.wait()

                # Make sure it exited cleanly
                try:
                    assert p.returncode == 0
                except AssertionError:
                    log.error("Error compiling bytecode with Vyper compiler on contract {}".format(
                        filename
                    ))
                    raise CompileError("Vyper compiler returned non-zero exit code: {}".format(
                        p.returncode
                    ))

            # ABI
            with abi_outfile.open(mode='wb') as out:
                abi_cmd = [
                    VYPER_PATH,
                    '-f',
                    'abi',
                    str(source_file)
                ]
                log.debug("Executing compiler with: {}".format(' '.join(abi_cmd)))

                # Execute and write output to outfile
                p = Popen(abi_cmd, bufsize=1, stdout=PIPE)
                for ln in p.stdout:
                    out.write(ln)
                p.wait()

                # Make sure it exited cleanly
                try:
                    assert p.returncode == 0
                except AssertionError:
                    log.error("Error building ABI with Vyper compiler on contract {}".format(
                        filename
                    ))
                    raise CompileError("Vyper compiler returned non-zero exit code: {}".format(
                        p.returncode
                    ))

        else:
            raise CompileError("Unsupported source file type")

    def compile_all(self):
        """ Compile a single contract with filename """

        log.debug("Compiling all contracts with compiler at {}".format(SOLC_PATH))
        log.debug("Contracts directory: {}".format(self.dir))
        log.debug("Build directory: {}".format(self.builddir))

        source_dir = Path(self.dir)

        contract_files = [f for f in source_dir.iterdir() if (source_dir.joinpath(f).is_file()
                                                              and supported_extension(f))]
        log.debug("contract files: {}".format(contract_files))

        for contract in contract_files:
            self.compile(contract)
