
import httplib2
import json
import sys


def jsonrpc(url, method, args):
    http = httplib2.Http()
    body = {'jsonrpc': '2.0', 'method': method, 'params': args}
    _body = json.dumps(body)
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json; charset=UTF-8',
    }
    response, content = http.request(url, 'POST', _body, headers=headers)
    return json.loads(content)



class GerritJSONRPC(object):
    def __init__(self, host, port, path):
        self.url = 'http://%s:%s%s' % (host, port, path)

    def _call(self, method, *args):
        response = jsonrpc(self.url, method, args)
        return response['result']

    def allQueryNext(self, search='', last_seen='z', page_size=25):
        data = self._call("allQueryNext", search, last_seen, page_size)
        reviews = data['changes']
        return [GerritJSONRPC._decode_review(review) for review in reviews]

    @staticmethod
    def _decode_review(data):
        return Review(review_id=data['id']['id'],
                      sort_key=data['sortKey'])



class Review(object):
    def __init__(self, **kwargs):
        self.review_id = kwargs.get('review_id')
        self.sort_key = kwargs.get('sort_key')

    def __repr__(self):
        args = (self.review_id, self.sort_key)
        return '<Review review_id=%s sort_key=%s>' % args


class Gerrit(object):
    def __init__(self, host, port, path):
        self.gerritjsonrpc = GerritJSONRPC(host, port, path)

    def reviews(self, status="open"):
        search = 'status: %s' % status
        last_seen = 'z'
        page_size = 25
        prev_length = page_size

        while page_size == prev_length:
            prev_length = 0
            reviews = self.gerritjsonrpc.allQueryNext(search,
                                                      last_seen,
                                                      page_size)

            for review in reviews:
                yield review
                last_seen = review.sort_key
                prev_length += 1


if __name__  == '__main__':
    server = Gerrit(sys.argv[1], sys.argv[2], '/gerrit/rpc/ChangeListService')
