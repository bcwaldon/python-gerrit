
from gerrit import model
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
                kwargs['last_seen'] = item['sortKey']
                current_page_size += 1

    def changes(self, status="open", project=None):
        search = 'status: %s' % status
        if project:
            search += ' project:%s' % (project.name,)
        _service = service.ChangeListService(self.host)
        for change in self._paginate(_service.allQueryNext, search):
            yield self._decode_change(change)

    def change(self, change_id):
        _service = service.ChangeDetailService(self.host)
        data = _service.changeDetail(change_id)
        return self._decode_change_details(data)

    def projects(self):
        _service = service.ProjectAdminService(self.host)
        for project in _service.visibleProjects():
            yield self._decode_project(project)

    def _decode_change(self, data):
        return model.Change(change_id=data['id']['id'],
                            sort_key=data['sortKey'])

    def _decode_change_details(self, data):
        #TODO: look up project description
        project = model.Project(name=data['dest']['projectName']['name'],
                                description='UNKNOWN')
        return model.ChangeDetails(change_id=data['changeId']['id'],
                                   sort_key=data['sortKey'],
                                   project=project)

    def _decode_project(self, data):
        return model.Project(name=data['name']['name'],
                             description=data['description'])
