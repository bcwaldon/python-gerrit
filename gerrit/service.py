
import httplib2
import json


def jsonrpc(url, method, args):
    http = httplib2.Http()
    body = {'jsonrpc': '2.0', 'method': method, 'params': args}
    _body = json.dumps(body)
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json; charset=UTF-8',
    }
    response, content = http.request(url, 'POST', _body, headers=headers)
    return json.loads(content)['result']


class BaseService(object):

    def __init__(self, host):
        self.url = '%s/%s' % (host, self.__class__.__name__)

    def _call(self, method, *args):
        return jsonrpc(self.url, method, args)


class ChangeListService(BaseService):

    def allQueryNext(self, search='', last_seen='z', page_size=25):
        data = self._call('allQueryNext', search, last_seen, page_size)
        return data['changes']


class ChangeDetailService(BaseService):

    def changeDetail(self, change_id):
        return self._call('changeDetail', {'id': change_id})['change']


class ProjectAdminService(BaseService):

    def visibleProjects(self):
        return self._call('visibleProjects')
