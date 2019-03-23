""" Solidity compilation utilities """
from typing import Any, Union
from pathlib import Path
from solidity_parser import parser
from ..common.utils import to_path


def parse_file(filepath: Path) -> Any:
    return parser.parse_file(str(filepath))


def is_solidity_interface_only(filepath: Union[str, Path]):
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
