from solidbyte.common.logging import setDebugLogging


def pytest_sessionstart(session):
    """ before session.main() is called. """
    setDebugLogging()
