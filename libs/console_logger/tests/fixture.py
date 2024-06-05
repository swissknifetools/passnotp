import logging
import pytest


@pytest.fixture
def log_record_debug():
    return logging.LogRecord(
        name="test_logger",
        level=logging.DEBUG,
        pathname="",
        lineno=0,
        msg="Debug message",
        args=None,
        exc_info=None,
    )


@pytest.fixture
def log_record_info():
    return logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Info message",
        args=None,
        exc_info=None,
    )


@pytest.fixture
def log_record_warning():
    return logging.LogRecord(
        name="test_logger",
        level=logging.WARNING,
        pathname="",
        lineno=0,
        msg="Warning message",
        args=None,
        exc_info=None,
    )


@pytest.fixture
def log_record_error():
    return logging.LogRecord(
        name="test_logger",
        level=logging.ERROR,
        pathname="",
        lineno=0,
        msg="Error message",
        args=None,
        exc_info=None,
    )


@pytest.fixture
def log_record_critical():
    return logging.LogRecord(
        name="test_logger",
        level=logging.CRITICAL,
        pathname="",
        lineno=0,
        msg="Critical message",
        args=None,
        exc_info=None,
    )
