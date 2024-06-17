import argparse

from libs.config.src.query.list_profile.handler import run as list_profile_qry


def get_profile_arguments():
    profile_parser = argparse.ArgumentParser(add_help=False)
    profile_parser.add_argument(
        "-p", "--profile", type=str, help="Profile of the entry.", default="default"
    )
    return profile_parser
