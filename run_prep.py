import re

from run_autodoc import create_autodoc

_regex = re.compile(r".*version.*\-.*\?\?\?")


def check_changelog():
    with open("CHANGELOG.md") as f:
        tx = f.read()
        if re.search(_regex, tx):
            print("check changelog")


if __name__ == "__main__":
    check_changelog()
    create_autodoc()
