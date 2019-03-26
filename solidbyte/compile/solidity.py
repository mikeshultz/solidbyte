""" Solidity compilation utilities """
from typing import Union
from pathlib import Path
from solidity_parser import parser
from ..common.utils import to_path


def parse_file(filepath: Path) -> dict:
    """ Parse a file using solidity_parser

    :param filepath: (:code:`str` or :class:`pathlib.Path`) Path to the source file to check
    :returns: (:code:`dict`) A Python dict representation of the source file
    """
    return parser.parse_file(str(filepath))


def is_solidity_interface_only(filepath: Union[str, Path]) -> bool:
    """ Given a path to a source file, check if the file only defines an :code:`interface`, but no
    other :code:`contract`.

    :param filepath: (:code:`str` or :class:`pathlib.Path`) Path to the source file to check
    :returns: (:code:`bool`) If it's recognize as a Solidity interface
    """
    filepath = to_path(filepath)
    source_dict = parse_file(filepath)
    has_contract = False
    has_interface = False

    if source_dict.get('children'):

        for top in source_dict['children']:
            if top.get('kind') == 'interface':
                has_interface = True
            if top.get('kind') == 'contract':
                has_contract = True

    if has_interface and not has_contract:
        return True

    return False
