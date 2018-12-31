import pytest
from solidbyte.console import (
    get_default_banner,
    SolidbyteConsole,
)
from .const import NETWORK_ID


def test_get_default_banner():
    """ Super useful test!  Way to shoot for coverage! """
    banner = get_default_banner(NETWORK_ID)
    assert type(banner) == str
    assert str(NETWORK_ID) in banner


@pytest.mark.skip(reason="How the hell is this even supposed to be tested?")
def test_console():
    """ Test the interactive console """
    sc = SolidbyteConsole()
    assert sc is not None
