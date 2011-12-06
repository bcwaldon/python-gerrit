"""
Direct Gerrit manipulation via its database.
"""

import sqlalchemy

class Client(object):
    def __init__(self, url):
        self.url = url
        self.engine = sqlalchemy.create_engine(url)
        self.meta = sqlalchemy.MetaData()
        self.meta.bind = self.engine
        self.conn = self.engine.connect()

        self.table_projects = sqlalchemy.Table('projects',
                                               self.meta,
                                               autoload=True)
        self.table_ref_rights = sqlalchemy.Table('ref_rights',
                                                 self.meta,
                                                 autoload=True)
        self.table_changes = sqlalchemy.Table('changes',
                                              self.meta,
                                              autoload=True)

    def project_exists(self, project):
        return bool(
                self.conn.execute(self.table_projects.select()\
                                      .where(self.table_projects.c.name \
                                              == project)))
    def create_project(self, project):
        self.conn.execute(self.table_projects.insert()\
                              .values(submit_type='M', name=project))

    def remove_project(self, project):
        self.conn.execute(self.table_projects.delete()\
                              .where(self.table_projects.c.name == project))
        self.conn.execute(self.table_ref_rights.delete()\
                              .where(self.table_ref_rights.c.project_name \
                                         == project))
        self.conn.execute(self.table_changes.delete()\
                              .where(self.table_changes.c.dest_project_name \
                                        == project))
        # FIXME: Delete all relevant data from all tables


