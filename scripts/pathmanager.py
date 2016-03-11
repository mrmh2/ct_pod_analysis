"""Helper class to manage paths for data."""

import os

HERE = os.path.dirname(__file__)
WORKING_BASE = os.path.join(HERE, '..', 'working')

class PathManager(object):

    def __init__(self, base_file_path, working_base=WORKING_BASE):
        self.rawpath = base_file_path
        self.basename = os.path.basename(base_file_path)
        self.name, self.ext = os.path.splitext(self.basename)
        self._basepath = os.path.join(working_base, self.name)

    @property
    def basepath(self):
        return self._basepath

    def spath(self, name):
        return os.path.join(self.basepath, name)
