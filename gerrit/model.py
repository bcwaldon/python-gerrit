
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

class BaseIdModel(BaseModel):
    def __hash__(self):
        return hash(self._cmp_key())

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented

        return self._cmp_key() == other._cmp_key()

class User(BaseModel):

    attributes = ('user_id', 'name')

    def __eq__(self, user):
        if not isinstance(user, User):
            return NotImplemented

        return self.user_id == user.user_id

class ChangeId(BaseModel):
    attributes = ('id',)

    @staticmethod
    def coerce(obj):
        if isinstance(obj, int):
            return ChangeId(id=obj)
        if isinstance(obj, ChangeId):
            return obj
        if isinstance(obj, PatchSetId):
            return obj.change_id
        if isinstance(obj, Change) or isinstance(obj, ChangeDetails):
            return obj.id
        if isinstance(obj, PatchSet) or isinstance(obj, PatchSetDetails):
            return obj.id.change_id
        return obj

    def to_json(self):
        return {'id': self.id}

class PatchSetId(BaseModel):
    attributes = ('id', 'change_id')

    @property
    def git_path(self):
      change_id = str(self.change_id.id)
      return 'refs/changes/%s/%s/%s' % (change_id[-2:], change_id, self.id)

    @staticmethod
    def coerce(obj):
        if isinstance(obj, PatchSetId):
            return obj
        if isinstance(obj, PatchSet) or isinstance(obj, PatchSetDetails):
            return obj.id
        return obj

    def to_json(self):
        return {'patchSetId': self.id,
                'changeId': self.change_id.to_json()}

class PatchId(BaseModel):
    attributes = ('path', 'patchset_id')

    @staticmethod
    def coerce(obj):
        if isinstance(obj, Patch):
            return obj.id
        return obj

    def to_json(self):
        return {'fileName': self.path,
                'patchSetId': self.patchset_id.to_json()}
    

class Project(BaseModel):
    attributes = ('name', 'description')


class Change(BaseModel):
    attributes = ('id', 'sort_key', 'name', 'project_name', 'last_updated_on')


class ChangeDetails(BaseModel):
    IN_PROGRESS = 'n'

    attributes = ('id', 'sort_key', 'project_name', 'name', 'message',
                  'status', 'last_patchset_details', 'patchsets', 'messages',
                  'last_updated_on')


class Message(BaseModel):
    attributes = ('message', )


class PatchSet(BaseModel):
    attributes = ('id', 'uploader')


class PatchSetDetails(BaseModel):
    attributes = ('id', 'uploader', 'name', 'message', 'patches')


class Permission(BaseModel):
    attributes = ('id', 'values')



class PatchSetPublishDetail(BaseModel):
    attributes = ('permissions', 'patchset_id')

    @classmethod
    def decode(cls, data):
      from decoder import decode_patchset_id

class Patch(BaseModel):
    MODIFIED = 'M'

    attributes = ('id', 'path', 'change_type', 'insertions', 'deletions')


class AccountId(BaseModel):
    attributes = ('id', )


class Account(BaseModel):
    attributes = ('id', 'user_name', 'full_name', 'email')
