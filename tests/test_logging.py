import logging
from solidbyte.common.logging import (
    parent_logger,
    console_handler,
    getLogger,
    setDebugLogging,
    loggingShutdown,
)


def test_logging():
    """ Test logging functionality """

    assert logging.DEBUG == parent_logger.getEffectiveLevel()

    testLogger = getLogger('test_logging')

    assert testLogger.name == 'test_logging'

    testLogger.debug("test debug")
    testLogger.info("test info")
    testLogger.warning("test warning")
    testLogger.error("test error")
    testLogger.critical("test critical")
    testLogger.exception("test exception")

    parent_logger.setLevel(logging.INFO)
    console_handler.setLevel(logging.INFO)

    assert logging.INFO == parent_logger.getEffectiveLevel()
    assert logging.INFO == console_handler.level

    setDebugLogging()

    assert logging.DEBUG == parent_logger.getEffectiveLevel()
    assert logging.DEBUG == console_handler.level

    loggingShutdown()

    try:
        parent_logger.info("debug - should fail")
        assert False, "Logging should have failed"
    except Exception:
        assert True
