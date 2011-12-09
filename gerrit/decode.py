
from gerrit import model
from datetime import datetime

def decode_datetime(data):
    # removing three trailing characters because of
    # different datetime precisions in Python and Java (6 vs 9)
    format = '%Y-%m-%d %H:%M:%S.%f'
    return datetime.strptime(data[:-3], format)

def decode_change(data):
    return model.Change(id=decode_change_id(data['id']),
                        sort_key=data['sortKey'],
                        name=data['subject'],
                        project_name=data['project']['key']['name'],
                        last_updated_on=decode_datetime(data['lastUpdatedOn']))

def decode_project(data):
    return model.Project(name=data['name']['name'],
                         description=data.get('description'))

def decode_change_details(data):
    #TODO: look up project description
    change = data['change']

    return model.ChangeDetails(id=decode_change_id(change['changeId']),
                               sort_key=change['sortKey'],
                               name=change['subject'],
                               message=data['currentDetail']['info']['message'].rstrip(),
                               project_name=change['dest']['projectName']['name'],
                               messages=[
                                 decode_message(message) for message in data['messages']
                                 ],
                               patchsets=[
                                 decode_patchset(patchset) for patchset in data['patchSets']],
                               last_patchset_details=decode_patchset_details(data['currentDetail']),
                               last_updated_on=decode_datetime(change['lastUpdatedOn']),
                               status=change['status'])

def decode_patchset(data):
    return model.PatchSet(id=decode_patchset_id(data['id']))

def decode_patchset_details(data):
    return model.PatchSetDetails(id=decode_patchset_id(data['patchSet']['id']),
                                 name=data['info']['subject'],
                                 message=data['info']['message'],
                                 patches=[
                                   decode_patch(patch) for patch in data['patches']])

def decode_message(data):
    return model.Message(message=data['message'])

def decode_patch(data):
    return model.Patch(id=decode_patch_id(data['key']),
                       path=data['key']['fileName'],
                       change_type=data['changeType'],
                       insertions=data['insertions'],
                       deletions=data['deletions'])

def decode_change_id(data):
    return model.ChangeId(id = data['id'])

def decode_patchset_id(data):
    return model.PatchSetId(id = data['patchSetId'],
                            change_id = decode_change_id(data['changeId']))

def decode_patch_id(data):
    return model.PatchId(path = data['fileName'],
                         patchset_id = decode_patchset_id(data['patchSetId']))

def decode_account_id(data):
    return model.AccountId(id = data['id'])

def decode_account(data):
    return model.Account(id = decode_account_id(data['accountId']),
                         user_name = data['userName'],
                         full_name = data['fullName'],
                         email = data['preferredEmail'])

def decode_permission(data):
    return model.Permission(id=data[0]['id'],
                            values=set(value['value'] for value in data[1]))

