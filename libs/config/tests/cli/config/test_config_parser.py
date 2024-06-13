import argparse

import pytest
from rich_argparse import RichHelpFormatter

from libs.config.src.cli.config.cli import add_config_cli


@pytest.fixture()
def parents():
    common_parser = argparse.ArgumentParser(add_help=False)
    common_options = common_parser.add_argument_group(title="global")

    common_options.add_argument(
        "-nc",
        "--no_color",
        action="store_true",
        default=False,
        help="disables color output",
    )

    return [common_parser]


def test_config_parser_default(parents):
    parser = argparse.ArgumentParser()
    parser_sp = parser.add_subparsers(title="commands", dest="command")
    add_config_cli(parser_sp, parents, True)
    args = parser.parse_args(["config"])
    assert args.func.__name__ == "print_help"
    assert args.command == "config"
    assert args.no_color is False

    config_parser = parser_sp.choices["config"]
    assert isinstance(config_parser.formatter_class, type(RichHelpFormatter))

    init_parser = config_parser._subparsers._group_actions[0].choices["init"]
    assert isinstance(init_parser.formatter_class, type(RichHelpFormatter))

    show_parser = config_parser._subparsers._group_actions[0].choices["show"]
    assert isinstance(show_parser.formatter_class, type(RichHelpFormatter))


def test_config_parser_init_args(parents):
    parser = argparse.ArgumentParser()
    parser_sp = parser.add_subparsers(title="commands", dest="command")
    add_config_cli(parser_sp, parents, True)
    args = parser.parse_args(["config", "init"])
    assert args.func.__name__ == "config_init"
    assert args.command == "config"
    assert args.subcommand == "init"
    assert args.no_color is False

    config_parser = parser_sp.choices["config"]
    assert isinstance(config_parser.formatter_class, type(RichHelpFormatter))

    init_parser = config_parser._subparsers._group_actions[0].choices["init"]
    assert isinstance(init_parser.formatter_class, type(RichHelpFormatter))

    show_parser = config_parser._subparsers._group_actions[0].choices["show"]
    assert isinstance(show_parser.formatter_class, type(RichHelpFormatter))


def test_config_parser_show_args(parents):
    parser = argparse.ArgumentParser()
    parser_sp = parser.add_subparsers(title="commands", dest="command")
    add_config_cli(parser_sp, parents, True)
    args = parser.parse_args(["config", "show"])
    assert args.func.__name__ == "config_show"
    assert args.command == "config"
    assert args.subcommand == "show"
    assert args.no_color is False

    config_parser = parser_sp.choices["config"]
    assert isinstance(config_parser.formatter_class, type(RichHelpFormatter))

    init_parser = config_parser._subparsers._group_actions[0].choices["init"]
    assert isinstance(init_parser.formatter_class, type(RichHelpFormatter))

    show_parser = config_parser._subparsers._group_actions[0].choices["show"]
    assert isinstance(show_parser.formatter_class, type(RichHelpFormatter))


def test_config_parser_color(parents):
    parser = argparse.ArgumentParser()
    parser_sp = parser.add_subparsers(title="commands", dest="command")
    add_config_cli(parser_sp, parents, False)
    args = parser.parse_args(["config"])
    assert args.func.__name__ == "print_help"
    assert args.command == "config"
    assert args.no_color is False

    config_parser = parser_sp.choices["config"]
    assert isinstance(config_parser.formatter_class, type(RichHelpFormatter))

    init_parser = config_parser._subparsers._group_actions[0].choices["init"]
    assert isinstance(init_parser.formatter_class, type(RichHelpFormatter))

    show_parser = config_parser._subparsers._group_actions[0].choices["show"]
    assert isinstance(show_parser.formatter_class, type(RichHelpFormatter))


def test_config_parser_no_color(parents):
    parser = argparse.ArgumentParser()
    parser_sp = parser.add_subparsers(title="commands", dest="command")
    add_config_cli(parser_sp, parents, False)
    args = parser.parse_args(["config", "--no_color"])
    assert args.func.__name__ == "print_help"
    assert args.command == "config"
    assert args.no_color is True

    config_parser = parser_sp.choices["config"]
    assert isinstance(config_parser.formatter_class, type(argparse.HelpFormatter))

    init_parser = config_parser._subparsers._group_actions[0].choices["init"]
    assert isinstance(init_parser.formatter_class, type(argparse.HelpFormatter))

    show_parser = config_parser._subparsers._group_actions[0].choices["show"]
    assert isinstance(show_parser.formatter_class, type(argparse.HelpFormatter))
