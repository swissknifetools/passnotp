import pathlib


class ConfigNotFound(Exception):
    def __init__(self, fp: pathlib.Path):
        self.fp = fp
        super().__init__(f"Config file {fp} not found!")
