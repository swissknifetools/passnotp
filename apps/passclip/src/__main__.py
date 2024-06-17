#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK

import argcomplete

from apps.passclip.src.app.core.logging import setup_logger
from apps.passclip.src.app.core.settings import settings
from apps.passclip.src.cli.common import get_common_parser
from apps.passclip.src.cli.main import get_main_parser
from libs.console_logger.src.constants import LogLevel


def main():
    common_parser = get_common_parser()
    common_args, extra = common_parser.parse_known_args()

    setup_logger(log_level=LogLevel[common_args.log_level], no_color=common_args.no_color)

    main_parser = get_main_parser(common_parser=common_parser, no_color=common_args.no_color)
    argcomplete.autocomplete(main_parser)
    args = main_parser.parse_args()
    args.settings = settings

    if args.func.__name__ == "print_help":
        args.func()
    else:
        args.func(args)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
