from pathlib import Path

from passclip.cli.passclip import cli


def main():
    cli()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
