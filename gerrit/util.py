
import os.path
import shutil
import subprocess
from collections import namedtuple
from pipes import quote

from gerrit import model

class ExecutionError(Exception):
    def __init__(self, cmd, stdin, code, out, err):
        self.cmd = cmd,
        self.stdin = stdin
        self.code = code
        self.out = out
        self.err = err

    def __str__(self):
        return '''
cmd: {cmd}
stdin: {stdin}
code: {code}
out: {out}
err: {err}
'''.format(**self.__dict__)

Execution = namedtuple('Execution', 'code out err')

def execute(cmd, stdin=None):
    process = subprocess.Popen(cmd,
                               shell = True,
                               stdin = subprocess.PIPE \
                                        if stdin is not None else None,
                               stdout = subprocess.PIPE,
                               stderr = subprocess.PIPE)

    out, err = process.communicate(stdin)
    return Execution(process.returncode, out, err)

def execute_assert(cmd, stdin=None):
    ret = execute(cmd, stdin)
    if ret.code:
        raise ExecutionError(
        cmd=cmd,
        stdin=stdin,
        code=ret.code,
        out=ret.out,
        err=ret.err)
    return ret

def reset_dir(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)

def download_patchset(patchset, target, repo_url):
    patchset = model.PatchSetId.coerce(patchset)

    cwd = os.getcwd()
    if not os.path.exists(target):
        os.makedirs(target)

    try:
        os.chdir(target)

        execute_assert('git init')
        execute_assert('git fetch %s %s' % (quote(repo_url),
                                            quote(patchset.git_path)))
        execute_assert('git checkout -f FETCH_HEAD')

    finally:
        os.chdir(cwd)
  


