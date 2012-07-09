"""
Gerrit RPC client implementation. This client
communicates with Gerrit using its JSON-RPC protocol.
It needs only HTTP access.
"""

from gerrit import model, error, decode, service
from urlparse import urljoin

class Client(object):

    def __init__(self, host):
        self.host = urljoin(host, 'gerrit/rpc')
        self.connection = service.Connection(self.host)

    def _paginate(self, method, *args, **kwargs):
        page_size = kwargs.get('page_size', 25)
        current_page_size = page_size
        kwargs['last_seen'] = 'z'
        while page_size == current_page_size:
            current_page_size = 0
            for item in method(*args, **kwargs):
                yield item
                kwargs['last_seen'] = item['sortKey']
                current_page_size += 1

    def authenticate(self, method, **kwargs):
      if method == 'user_pass':
        _service = service.UserPassAuthService(self.connection)
        _service.authenticate(kwargs['username'], kwargs['password'])
      elif method == 'become':
        _service = service.BecomeAuthService(self.connection)
        _service.authenticate(kwargs['username'])
      else:
        raise error.UnknownAuthenticationMethodError()
        
    def changes(self, status="open", **search):
        result = []

        query = 'status:%s' % status

        for key, value in search.iteritems():
            query += ' %s:%s' % (key, value)

        _service = service.ChangeListService(self.connection)
        for change in self._paginate(_service.allQueryNext, query):
            result.append(decode.decode_change(change))

        return result

    def change_details(self, change):
        change = model.ChangeId.coerce(change)

        _service = service.ChangeDetailService(self.connection)
        data = _service.changeDetail(change)
        return decode.decode_change_details(data)

    def patchset_details(self, patchset):
        patchset = model.PatchSetId.coerce(patchset)

        _service = service.ChangeDetailService(self.connection)
        data = _service.patchSetDetail(patchset)
        return decode.decode_patchset_details(data)

    def publish_review(self, patchset, comment):
        patchset = model.PatchSetId.coerce(patchset)

        _service = service.PatchDetailService(self.connection)
        _service.publishComments(patchset, comment, [])

    def save_comment(self, patch, line, message, timestamp=None):
        patch = model.PatchId.coerce(patch)

        _service = service.PatchDetailService(self.connection)
        _service.saveDraft(patch, line, message, timestamp = timestamp)

    def projects(self):
        result = []

        _service = service.ProjectAdminService(self.connection)
        for project in _service.visibleProjects():
            result.append(decode.decode_project(project))

        return result

    def account(self):
        _service = service.AccountService(self.connection)
        try:
            return decode.decode_account(_service.myAccount())
        except error.NotSignedInError:
            return None

