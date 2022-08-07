import os
from setuputil import do_main_import

os.chdir(os.path.dirname(__file__))

mod = do_main_import()
mod.main_func()

