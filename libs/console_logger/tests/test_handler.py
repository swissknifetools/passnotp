import logging

from requests import get

from libs.console_logger.src import (
    ColoredFormatter,
    ConsoleHandler,
    get_console_handler,
)
from libs.console_logger.src.constants import LogLevel, LogLevelColor
from libs.console_logger.tests.fixture import (
    log_record_critical,
    log_record_debug,
    log_record_error,
    log_record_info,
    log_record_warning,
)


def test_get_console_handler_default():
    handler = get_console_handler()
    assert isinstance(handler, ConsoleHandler)
    assert handler.level == getattr(logging, LogLevel.INFO)
    assert isinstance(handler.formatter, ColoredFormatter)
    assert handler.formatter.use_color is True


def test_get_console_handler_args():
    handler = get_console_handler(log_level=LogLevel.DEBUG, use_color=False)
    assert isinstance(handler, ConsoleHandler)
    assert handler.level == getattr(logging, LogLevel.DEBUG)
    assert isinstance(handler.formatter, ColoredFormatter)
    assert handler.formatter.use_color is False


def test_colored_formatter_no_color(log_record_info):
    formatter = ColoredFormatter(fmt="%(asctime)s - %(message)s", use_color=False)
    log_entry = formatter.format(log_record_info)
    assert log_entry == f"INFO {log_record_info.asctime} - {log_record_info.message}"


def test_colored_formatter_with_color_debug(log_record_debug):
    formatter = ColoredFormatter(fmt="%(asctime)s - %(message)s", use_color=True)
    log_entry = formatter.format(log_record_debug)
    expected_output = f"{LogLevelColor.DEBUG.value}[DEBUG]{LogLevelColor.RESET.value} {LogLevelColor.WHITE.value}{log_record_debug.asctime}{LogLevelColor.RESET.value} - {log_record_debug.message}"
    assert log_entry == expected_output


def test_colored_formatter_with_color_info(log_record_info):
    formatter = ColoredFormatter(fmt="%(asctime)s - %(message)s", use_color=True)
    log_entry = formatter.format(log_record_info)
    expected_output = f"{LogLevelColor.INFO.value}[INFO]{LogLevelColor.RESET.value} {LogLevelColor.WHITE.value}{log_record_info.asctime}{LogLevelColor.RESET.value} - {log_record_info.message}"
    assert log_entry == expected_output


def test_colored_formatter_with_color_warning(log_record_warning):
    formatter = ColoredFormatter(fmt="%(asctime)s - %(message)s", use_color=True)
    log_entry = formatter.format(log_record_warning)
    expected_output = f"{LogLevelColor.WARNING.value}[WARNING]{LogLevelColor.RESET.value} {LogLevelColor.WHITE.value}{log_record_warning.asctime}{LogLevelColor.RESET.value} - {log_record_warning.message}"
    assert log_entry == expected_output


def test_colored_formatter_with_color_error(log_record_error):
    formatter = ColoredFormatter(fmt="%(asctime)s - %(message)s", use_color=True)
    log_entry = formatter.format(log_record_error)
    expected_output = f"{LogLevelColor.ERROR.value}[ERROR]{LogLevelColor.RESET.value} {LogLevelColor.WHITE.value}{log_record_error.asctime}{LogLevelColor.RESET.value} - {log_record_error.message}"
    assert log_entry == expected_output


def test_colored_formatter_with_color_critical(log_record_critical):
    formatter = ColoredFormatter(fmt="%(asctime)s - %(message)s", use_color=True)
    log_entry = formatter.format(log_record_critical)
    expected_output = f"{LogLevelColor.CRITICAL.value}[CRITICAL]{LogLevelColor.RESET.value} {LogLevelColor.WHITE.value}{log_record_critical.asctime}{LogLevelColor.RESET.value} - {log_record_critical.message}"
    assert log_entry == expected_output


def test_console_handler_respects_log_level(capsys):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = get_console_handler(log_level=LogLevel.WARNING, use_color=True)
    logger.addHandler(handler)

    logger.debug("Debug message")
    captured = capsys.readouterr()
    assert captured.out == ""

    logger.debug("Info message")
    captured = capsys.readouterr()
    assert captured.out == ""

    logger.warning("Warning message")
    captured = capsys.readouterr()
    assert captured.out.startswith(
        f"{LogLevelColor.WARNING.value}[WARNING]{LogLevelColor.RESET.value}"
    )
    assert captured.out.endswith("- Warning message\n")

    logger.error("Error message")
    captured = capsys.readouterr()
    assert captured.out.startswith(f"{LogLevelColor.ERROR.value}[ERROR]{LogLevelColor.RESET.value}")
    assert captured.out.endswith("- Error message\n")

    logger.critical("Critical message")
    captured = capsys.readouterr()
    assert captured.out.startswith(
        f"{LogLevelColor.CRITICAL.value}[CRITICAL]{LogLevelColor.RESET.value}"
    )
    assert captured.out.endswith("- Critical message\n")
