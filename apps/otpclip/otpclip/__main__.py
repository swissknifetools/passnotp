from otpclip.app.core.db.engine import engine
from otpclip.cli.otp import cli_otp


def main() -> None:
    cli_otp()


if __name__ == "__main__":
    try:
        conn = engine.connect()
        print(conn)
    except Exception as e:
        print(e)
    main()
