import subprocess
import sys


def main():
    try:
        result = subprocess.run(["black", "."], check=True)
        sys.exit(result.returncode)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)


if __name__ == "__main__":
    main()
