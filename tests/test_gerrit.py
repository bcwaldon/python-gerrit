"""

CAVEAT EMPTOR: Tests require to be launched top-down!

Notes:
    If you inspect Gerrit manually after running these
"""

from __future__ import print_function

import pytest

import fixtures
from gerrit import Client, ChangeDetails, Patch, AuthenticationError

def setup_module():
    fixtures.setup()

def gerrit():
    return Client('http://localhost:8080')

def authenticated_gerrit():
    client = gerrit()
    client.authenticate(method = 'become', username = fixtures.USERNAME)
    return client

def first_line(text):
    return text.strip().split('\n')[0].strip()

def first_para(text):
    lines = [line.strip() for line in text.strip().split('\n')]
    result = []
    for line in lines:
        if not line:
            return ' '.join(result)
        result.append(line)
    return ' '.join(result)

def test_projects():
    client = gerrit()

    projects = client.projects()
    assert any(project.name == fixtures.TEST_PROJECT for project in projects)

def test_changes():
    client = gerrit()

    changes = client.changes(project = fixtures.TEST_PROJECT)
    assert set(change.name for change in changes) == \
            set((first_para(fixtures.COMMIT_i),
                 first_para(fixtures.COMMIT_b1_2),
                 first_para(fixtures.COMMIT_b2),))
    assert changes[0].project_name == fixtures.TEST_PROJECT

def test_change_details():
    client = gerrit()

    # We need to get the id at a cost of a slightly more brittle test
    changes = client.changes(project = fixtures.TEST_PROJECT)
    change = [ch for ch in changes if ch.name == first_para(fixtures.COMMIT_b2)][0]

    change = client.change_details(change)
    print(change)
    assert change.name == first_para(fixtures.COMMIT_b2)
    assert change.message == fixtures.COMMIT_b2
    assert change.status == ChangeDetails.IN_PROGRESS
    assert len(change.messages) == 0

def test_patchset_details():
    client = gerrit()

    # We need to get the id at a cost of a slightly more brittle test
    changes = client.changes(project = fixtures.TEST_PROJECT)
    change = [ch for ch in changes if ch.name == first_para(fixtures.COMMIT_b1_2)][0]

    change = client.change_details(change)
    patchset = change.last_patchset_details
    assert len(patchset.patches) == 2
    assert patchset.patches[-1].change_type == Patch.MODIFIED
    assert patchset.patches[-1].insertions == 5
    assert patchset.patches[-1].deletions == 1


def test_review():
    client = authenticated_gerrit()
    REVIEW_COMMENT = "YES, THIS IS COMMENT"

    # We need to get the id at a cost of a slightly more brittle test
    changes = client.changes(project = fixtures.TEST_PROJECT)
    change = [ch for ch in changes if ch.name == first_para(fixtures.COMMIT_b2)][0]

    change = client.change_details(change)
    patchset = change.last_patchset_details
    client.publish_review(patchset, REVIEW_COMMENT)

    change = client.change_details(change)
    assert len(change.messages) == 1
    assert change.messages[0].message.strip().endswith(REVIEW_COMMENT)

def test_commenting():
    client = authenticated_gerrit()

    # We need to get the id at a cost of a slightly more brittle test
    changes = client.changes(project = fixtures.TEST_PROJECT)
    change = [ch for ch in changes if ch.name == first_para(fixtures.COMMIT_b2)][0]

    change = client.change_details(change)
    patchset = change.last_patchset_details
    client.save_comment(patchset.patches[-1], 2, 'Hello!')
    return #FIXME: actually do some testing here!

# skipping - if someone has any idea how to create a simple LDAP server,
#            leave me a note
def _test_invalid_authentication():
    client = gerrit()

    with pytest.raises(AuthenticationError):
        client.authenticate(method = 'user_pass',
                            username = fixtures.USERNAME,
                            password = fixtures.PASSWORD+'___')

# skipping - see note above
def _test_authentication():
    client = gerrit()

    client.authenticate(method = 'user_pass',
                      username = fixtures.USERNAME,
                      password = fixtures.PASSWORD)

def test_account_without_signing_in():
    client = gerrit()

    assert client.account() is None

def test_dev_authentication():
    client = gerrit()

    client.account()
    client.authenticate(method = 'become',
                      username = fixtures.USERNAME)

    assert client.account().user_name == fixtures.USERNAME


      

