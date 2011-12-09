
from pipes import quote
import os.path
from gerrit.util import reset_dir, execute_assert
from gerrit import db, raw

assert os.getenv('GERRIT_GIT')
assert os.getenv('GERRIT_URL')
assert os.getenv('GERRIT_DB')
assert os.getenv('GERRIT_PATH')
assert os.getenv('GERRIT_USERNAME')

TEST_PROJECT = 'python-gerrit-test-project'
GERRIT_URL = os.getenv('GERRIT_URL')
GERRIT_GIT = os.getenv('GERRIT_GIT').rstrip('/') + '/' + TEST_PROJECT
GERRIT_DB = os.getenv('GERRIT_DB')
GERRIT_PATH = os.getenv('GERRIT_PATH')
FIXTURE_DIR = '_fixture'
USERNAME = os.getenv('GERRIT_USERNAME')

FILE1 = 'foo'
FILE2 = 'bar'
FILE3 = 'fubar'

COMMIT_i = 'initial'
COMMIT_b1 = '''second commit
with multiline message!

Change-Id: Ic8aaa0728a43936cd4c6e1ed590e01ba8f0fbf5b
'''
COMMIT_b1_2 = '''patchset #2

Many paragraph, this one has.

Yoda says.

Change-Id: Ic8aaa0728a43936cd4c6e1ed590e01ba8f0fbf5b
'''
COMMIT_b2 = 'another branch'

FILE1_i = """
hello world!
"""
FILE1_b1 = """
second commit
"""
FILE1_b1_2 = """
second commit
second commit
second commit
second commit
or maybe third...
"""

FILE2_i = """
hello world from second file.
"""
FILE2_b2 = """
hello world from second file.
hello world from second file.
"""
FILE3_b2 = """
third file
"""

class ChangeCwd(object):
    def __init__(self, path):
        self.path = path

    def __enter__(self):
        self.old_path = os.getcwd()
        os.chdir(self.path)
        return self

    def __exit__(self, *args):
        os.chdir(self.old_path)

class TestGitRepo(object):
    def __init__(self, path, remote=None):
        self.path = path
        self.remote = remote

    def _execute(self, *args):
        execute_assert(' '.join(quote(x) for x in args))

    def clear(self):
        reset_dir(self.path)
        with ChangeCwd(self.path):
            self._execute('git', 'init')

    def set_content(self, **files):
        with ChangeCwd(self.path):
            for path, content in files.items():
                file = open(path, 'w')
                file.write(content)
                file.close()
                self._execute('git', 'add', path)

    def commit(self, message, amend = False):
        with ChangeCwd(self.path):
            if amend:
                self._execute('git', 'commit', '--amend', '-m', message)
            else:
                self._execute('git', 'commit', '-m', message)

    def make_branch(self, branch):
        with ChangeCwd(self.path):
            self._execute('git', 'checkout', '-b', branch)

    def checkout_branch(self, branch):
        with ChangeCwd(self.path):
            self._execute('git', 'checkout', branch)

    def push_to_gerrit(self):
        with ChangeCwd(self.path):
            self._execute('git', 'push', self.remote, 'HEAD:refs/for/master')

def set_content(path, content):
    open(path, 'w').write(content)

def setup():
    # Recreating Gerrit project
    db_client = db.Client(GERRIT_DB)
    raw_client = raw.Client(GERRIT_PATH)
    
    if db_client.project_exists(TEST_PROJECT):
        db_client.remove_project(TEST_PROJECT)
    if raw_client.project_exists(TEST_PROJECT):
        raw_client.remove_project(TEST_PROJECT)

    db_client.create_project(TEST_PROJECT)
    raw_client.create_project(TEST_PROJECT)

    # Creating git repo
    repo = TestGitRepo(FIXTURE_DIR, GERRIT_GIT)
    repo.clear()

    # Adding some random commits
    repo.set_content(FILE1 = FILE1_i,
                     FILE2 = FILE2_i)
    repo.commit(COMMIT_i)

    repo.push_to_gerrit()

    repo.make_branch('b1')
    repo.set_content(FILE1 = FILE1_b1)
    repo.commit(COMMIT_b1)
    repo.push_to_gerrit()

    repo.set_content(FILE1 = FILE1_b1_2)
    repo.commit(COMMIT_b1_2, amend = True)
    repo.push_to_gerrit()

    repo.checkout_branch('master')
    repo.make_branch('b2')
    repo.set_content(FILE2 = FILE2_b2,
                     FILE3 = FILE3_b2)
    repo.commit(COMMIT_b2)
    repo.push_to_gerrit()

if __name__ == '__main__':
    setup()
