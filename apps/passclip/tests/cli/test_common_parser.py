import pytest

from apps.passclip.src.cli.common import get_common_parser


def test_common_parser_defaults():
    parser = get_common_parser()
    args = parser.parse_args([])
    assert args.log_level == "INFO"
    assert args.no_color is False


def test_common_parser_args():
    parser = get_common_parser()
    args = parser.parse_args(["-l", "DEBUG", "-nc"])
    assert args.log_level == "DEBUG"
    assert args.no_color is True

    args = parser.parse_args(["--log_level", "WARNING"])
    assert args.log_level == "WARNING"
    assert args.no_color is False

    args = parser.parse_args(["--no_color"])
    assert args.log_level == "INFO"
    assert args.no_color is True


def test_invalid_log_level():
    parser = get_common_parser()

    with pytest.raises(SystemExit):
        parser.parse_args(["--log_level", "INVALID"])
