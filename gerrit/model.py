
class BaseModel(object):

    attributes = ()

    def __init__(self, **kwargs):
        for (k, v) in kwargs.items():
            setattr(self, k, v)

    def __setattr__(self, key, value):
        if key in self.__class__.attributes or key in self.__dict__:
            self.__dict__[key] = value
        else:
            raise AttributeError(key)

    def __getattr__(self, key):
        try:
            return self.__dict__[key]
        except KeyError:
            if key in self.__class__.attributes:
                return None
            else:
                raise AttributeError(key)

    def __repr__(self):
        key = self.__class__.attributes[0]
        value = getattr(self, key)
        return '<%s %s=%s>' % (self.__class__.__name__, key, value)


class Project(BaseModel):

    attributes = ('name', 'description')


class Change(BaseModel):

    attributes = ('change_id', 'sort_key')


class ChangeDetails(BaseModel):

    attributes = ('change_id', 'sort_key', 'project')
