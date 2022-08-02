import sys
import os
import re
import subprocess

from setuputil import find_projectname


class AutoDoc(object):
    """create markdown of cmd-line"""

    def __init__(self, cmd_tool=None, extreadme="_"):
        self.rst()

        if cmd_tool is None:
            cmd_tool = find_projectname()

        self.cmd_tool = cmd_tool
        self.extreadme = extreadme

    def doc(self):
        return self._doc

    def rst(self):
        self._doc = ""

    def pr(self, *args):
        d = ""
        for s in args:
            self._doc += d
            self._doc += s
            d = "\t"
        self._doc += "\n"

    def create(self):

        self.rst()

        self.pr("")
        self.pr(f"# all `{self.cmd_tool}` cmd-line options")
        self.pr("")

        args = ["python3", "-m", self.cmd_tool, "-h"]
        rc = subprocess.run(args, capture_output=True)
        if rc.returncode:
            raise Exception(rc)

        s = rc.stdout.decode()

        _regex = r"{(.*)}"
        matches = re.finditer(_regex, s, re.MULTILINE)

        scancmd = [""]

        for m in matches:
            scancmd.extend(m.group(1).split(","))

        print("found", scancmd)

        for idx, cmd in enumerate(scancmd):

            args = ["python3", "-m", self.cmd_tool, cmd, "-h"]
            args = list(filter(lambda x: len(x), args))
            rc = subprocess.run(args, capture_output=True)

            if rc.returncode:
                raise Exception(rc)

            cmd = " ".join(args[2:-1])
            cmd_ = cmd.replace(" ", "_").replace("-", "")

            self.pr("")
            self.pr(f"## {cmd}")
            self.pr("")
            self.pr(f"run `{cmd} -h` for help")
            self.pr("")
            lines = rc.stdout.decode().splitlines()

            for line in lines:
                self.pr(" " * 4 + line)

            self.pr("")

        return self

    def write(self):
        with open(f"README{self.extreadme}CMDLINE.md", "w") as f:
            f.write(self._doc)

    def create_autodoc(self):
        self.create()
        self.write()


def create_autodoc():
    AutoDoc().create_autodoc()


if __name__ == "__main__":
    create_autodoc()
