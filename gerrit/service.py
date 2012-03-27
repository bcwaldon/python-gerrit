
import httplib2
import json
import datetime
from urlparse import urljoin
from Cookie import SimpleCookie
from error import AuthenticationError, GerritError, NotSignedInError

class Connection(object):
    def __init__(self, host):
          self.host = host
          self.cookie = ''
          self.xsrf_key = None

          self.http = httplib2.Http()
          self.http.follow_redirects = False
          self.http.follow_all_redirects = False

    def request(self, url, body=None, method='POST'):
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json; charset=UTF-8',
            'Cookie': self.cookie,
        }

        response, content = self.http.request(url, method, body, headers=headers)
        if 'set-cookie' in response:
          self.cookie = response['set-cookie']
          cookie = SimpleCookie()
          cookie.load(self.cookie)
          self.xsrf_key = cookie['GerritAccount'].value

        return response, content

class Service(object):
    def __init__(self, connection):
        self.connection = connection
        self.url = urljoin(self.connection.host+'/', self.__class__.__name__)

    def _request(self, *args, **kwargs):
        return self.connection.request(*args, **kwargs)

    def _call(self, method, *params):
        body = {'jsonrpc': '2.0', 'method': method, 'params': params}
        if self.connection.xsrf_key:
            body['xsrfKey'] = self.connection.xsrf_key
        body = json.dumps(body)
        data = json.loads(self._request(self.url, body)[1])

        if 'error' in data:
            error = GerritError
            if data['error']['message'] == 'Not Signed In':
                error = NotSignedInError

            raise error(data['error']['message'])

        return data['result']

class ChangeListService(Service):
    def allQueryNext(self, search='', last_seen='z', page_size=25):
        data = self._call('allQueryNext', search, last_seen, page_size)
        return data['changes']


class ChangeDetailService(Service):
    def changeDetail(self, change_id):
        return self._call('changeDetail', change_id.to_json())

    def patchSetDetail(self, patchset_id):
        return self._call('patchSetDetail', patchset_id.to_json(), None, None)

class PatchDetailService(Service):
    def publishComments(self, patchset_id, comment, votes):
        return self._call('publishComments',
                          patchset_id.to_json(),
                          comment,
                          votes)

    def patchScript(self, patch_id, patchset_id, diff_base_id = None, diff_prefs=None):
        # FIXME: complete me
        return self._call('patchScript',
                          patch_id.to_json(),
                          diff_base_id.to_json() if diff_base_id else None,
                          patchset_id.to_json(),
                          None)

    def saveDraft(self, patch_id, line, message, side = 1, timestamp = None):
        if not timestamp:
            timestamp = datetime.datetime.now()

        return self._call('saveDraft', {'key': {'patchKey': patch_id.to_json()},
                                        'lineNbr': line,
                                        'message': message,
                                        'writtenOn': str(timestamp),
                                        'status': 'd',  # draft
                                        'side': side,
                                        })


class ProjectAdminService(Service):
    def visibleProjects(self):
        return self._call('visibleProjects')

class AccountService(Service):
    def myAccount(self):
        return self._call('myAccount')


class UserPassAuthService(Service):
    def authenticate(self, username, password):
        data = self._call('authenticate', username, password)
        if not data['success']:
          raise AuthenticationError()


class BecomeAuthService(Service):
    def authenticate(self, username):
        response, content = self._request(urljoin(self.connection.host, '/become?user_name=' + username), method='GET')
        if response.status != 302:
          raise AuthenticationError(content)
