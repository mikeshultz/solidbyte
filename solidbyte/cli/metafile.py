""" show version information
"""
import sys
from pathlib import Path
from ..common import collapse_oel
from ..common.logging import getLogger
from ..common.metafile import MetaFile

log = getLogger(__name__)


def add_parser_arguments(parser):

    parser.add_argument('-f', '--file', metavar="METAFILE", type=str,
                        help='The metafile to perform operations on')

    subparsers = parser.add_subparsers(title='Metafile Commands',
                                       dest='metafile_command',
                                       help='Perform various MetaFile operations')

    cleanup_parser = subparsers.add_parser('cleanup',
                                           help="Cleanup test deployments in metafile.json")
    cleanup_parser.add_argument('--dry-run', dest='dry_run', action='store_true',
                                help='The location of the backup file')

    backup_parser = subparsers.add_parser('backup', help="Backup metafile.json")
    backup_parser.add_argument('destfile', metavar='DESTFILE', type=str, nargs=1,
                               help='The location of the backup file')

    return parser


def main(parser_args):
    """ Open an interactive solidbyte console """

    if hasattr(parser_args, 'file') and parser_args.file:
        file_path = Path(parser_args.file)
    else:
        file_path = Path.cwd().joinpath('metafile.json')

    metafile = MetaFile(filename_override=file_path.name, project_dir=file_path.parent)

    if parser_args.metafile_command == 'cleanup':

        # TODO: Are you sure? prompt
        removed_deployments = metafile.cleanup(parser_args.dry_run)
        if len(removed_deployments) > 0:
            for depl in removed_deployments:
                if parser_args.dry_run:
                    action = 'Would have removed'
                else:
                    action = 'Removed'
                log.info("{} deployment {} (network_id: {})".format(
                    action,
                    depl[0],
                    depl[1],
                ))
        else:
            log.warning("No entries removed from metafile.json")

    elif parser_args.metafile_command == 'backup':
        destfile = Path(collapse_oel(parser_args.destfile))
        log.info("Copying {} to {}...".format(
            file_path,
            destfile
        ))
        success = metafile.backup(destfile)
        if success:
            log.info("Complete. Backup located at {}.".format(destfile))
        else:
            log.error("Backup failed!")

    else:
        log.warning("Command required")
        sys.exit(1)
