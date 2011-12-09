"""
Direct Gerrit manipulation via its database.
"""

import sqlalchemy

class UnsupportedDatabaseSchema(object):
    def __init__(self, version):
        self.version = version

    def __str__(self):
        return 'This object supports databases only of Gerrit 2.1.8 or lower.'

class Client(object):
    MAX_SUPPORTED_SCHEMA = 52

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
        self.table_schema_version = sqlalchemy.Table('schema_version',
                                                     self.meta,
                                                     autoload=True)

        self._check_schema()

    def _check_schema(self):
        row = self.conn.execute(self.table_schema_version.select()).first()
        version = row['version_nbr']

        if version > self.MAX_SUPPORTED_SCHEMA:
            raise UnsupportedDatabaseSchema(version)


    def project_exists(self, project):
        return bool(
                self.conn.execute(self.table_projects.select()\
                                      .where(self.table_projects.c.name \
                                              == project)).first())
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


