
import httplib2
import json

from gerrit import model


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
        reviews = data['changes']
        return [ChangeListService._decode_review(review) for review in reviews]

    @staticmethod
    def _decode_review(data):
        return model.Review(review_id=data['id']['id'],
                            sort_key=data['sortKey'])


class ProjectAdminService(BaseService):

    def visibleProjects(self):
        data = self._call('visibleProjects')
        return [ProjectAdminService._decode_project(datum) for datum in data]

    @staticmethod
    def _decode_project(data):
        return model.Project(name=data['name']['name'],
                             description=data['description'])
