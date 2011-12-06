"""
Gerrit client operating on raw filesystem.
"""
import os.path
import shutil

from pipes import quote
from StringIO import StringIO
from ConfigParser import ConfigParser
from gerrit.util import execute_assert

class Client(object):
    def __init__(self, path):
        self.path = path
        self._read_config(os.path.join(path, 'etc', 'gerrit.config'))

    def _read_config(self, path):
        # Whitespace removal, as ConfigParser is rather
        # picky when it comes to syntax.
        content = open(path).read()
        content = '\n'.join(line.strip() for line in content.split('\n'))
        filelike = StringIO(content)

        config = ConfigParser()
        config.readfp(filelike)
        self.git_base_path = os.path.join(self.path,
                                          config.get('gerrit', 'basePath'))
    
    def project_path(self, project):
        return os.path.join(self.git_base_path, project) + '.git'

    def project_exists(self, project):
        return os.path.exists(self.project_path(project))

    def remove_project(self, project):
        shutil.rmtree(self.project_path(project))

    def create_project(self, project):
        execute_assert('git %s init' % quote('--git-dir=' + \
                                             self.project_path(project)))
        

