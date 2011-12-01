
from gerrit import service


class Gerrit(object):

    def __init__(self, host):
        self.host = host

    def _paginate(self, method, *args, **kwargs):
        page_size = kwargs.get('page_size', 25)
        current_page_size = page_size
        kwargs['last_seen'] = 'z'
        while page_size == current_page_size:
            current_page_size = 0
            for item in method(*args, **kwargs):
                yield item
                kwargs['last_seen'] = item.sort_key
                current_page_size += 1

    def reviews(self, status="open", project=None):
        search = 'status: %s' % status
        if project:
            search += ' project:%s' % (project.name,)
        _service = service.ChangeListService(self.host)
        for review in self._paginate(_service.allQueryNext, search):
            yield review

    def projects(self):
        _service = service.ProjectAdminService(self.host)
        for project in _service.visibleProjects():
            yield project
