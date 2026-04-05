from importlib.resources import files


def load_prompt(package: str, filename: str) -> str:
    return files(package).joinpath(filename).read_text()
