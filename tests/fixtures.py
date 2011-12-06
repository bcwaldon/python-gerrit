
from __future__ import print_function

from pipes import quote
import os.path
from gerrit.util import reset_dir, execute_assert
from gerrit import db, raw

assert os.getenv('GERRIT_GIT')
assert os.getenv('GERRIT_DB')
assert os.getenv('GERRIT_PATH')
assert os.getenv('GERRIT_USERNAME')

TEST_PROJECT = 'python-gerrit-test-project'
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

def set_content(path, content):
    open(path, 'w').write(content)

def setup():
    db_client = db.Client(GERRIT_DB)
    raw_client = raw.Client(GERRIT_PATH)
    
    if db_client.project_exists(TEST_PROJECT):
        db_client.remove_project(TEST_PROJECT)
    if raw_client.project_exists(TEST_PROJECT):
        raw_client.remove_project(TEST_PROJECT)

    db_client.create_project(TEST_PROJECT)
    raw_client.create_project(TEST_PROJECT)

    # Creating git repo
    reset_dir(FIXTURE_DIR)
    os.chdir(FIXTURE_DIR)
    execute_assert('git init')
    git_url = quote(GERRIT_GIT)

    # Adding some random commits
    set_content(FILE1, FILE1_i)
    set_content(FILE2, FILE2_i)
    execute_assert('git add .')
    execute_assert('git commit -m ' + quote(COMMIT_i))

    print('[1/4] Pushing')
    execute_assert('git push %s HEAD:refs/for/master' % git_url)

    execute_assert('git checkout -b b1')
    set_content(FILE1, FILE1_b1)
    execute_assert('git commit -am ' + quote(COMMIT_b1))

    print('[2/4] Pushing')
    execute_assert('git push %s HEAD:refs/for/master' % git_url)

    set_content(FILE1, FILE1_b1_2)
    execute_assert('git commit --amend -am ' + quote(COMMIT_b1_2))

    print('[3/4] Pushing')
    execute_assert('git push %s HEAD:refs/for/master' % git_url)

    execute_assert('git checkout master')
    execute_assert('git checkout -b b2')
    set_content(FILE2, FILE2_b2)
    set_content(FILE3, FILE3_b2)
    execute_assert('git add .')
    execute_assert('git commit -am ' + quote(COMMIT_b2))

    print('[4/4] Pushing')
    execute_assert('git checkout b2')
    execute_assert('git push %s HEAD:refs/for/master' % git_url)

if __name__ == '__main__':
  setup()
