#!/usr/bin/python
# -*- coding: utf-8 -*-

import pdb

import os as mod_os
import os.path as mod_path
import sys as mod_sys
import subprocess as mod_subprocess
import tempfile as mod_tempfile
import re as mod_re

def assert_in_git_repository():
    rc, lines = execute_git(['status'], output=False)
    if rc != 0:
        print 'Not a git repository!!!'
        print lines
        mod_sys.exit(1)

class ExecuteCommand(object):
    '''Class to execute a command as a subprocess.

    The class encapsulation allows running multiple commands in
    parallel.
    '''
    def __init__(self, command):
        self.command = command

        self.proc = None
        self.rc = None
        self.output = None

        self.tempfile = mod_tempfile.NamedTemporaryFile(prefix='multigit-',
                                                        dir='/tmp')
        self.proc = mod_subprocess.Popen(command,
                                         stdout=self.tempfile,
                                         stderr=mod_subprocess.STDOUT)

    def wait(self):
        if self.proc is not None:
            self.rc = self.proc.wait()
            self.proc = None

        return self.rc

    def read(self):
        self.tempfile.file.seek(0)
        return self.tempfile.read()

    def readline(self):
        return self.tempfile.readline()

    def readlines(self):
        self.tempfile.file.seek(0)
        for line in self.tempfile.readlines():
            yield line

    def grep(self, regex):
        re_grep = mod_re.compile(regex)
        for line in self.readlines():
            if re_grep.match(line):
                yield line

    def result(self, do_output=True, prefix='', grep=None):
        result = []
        for line in self.readlines():
            if not grep or grep in line:
                line = prefix + line.rstrip()
                result.append(line)
                if do_output:
                    print line
                    mod_sys.stdout.flush()
        return '\n'.join(result)

    def close(self):
        if not self.tempfile.close_called:
            self.tempfile.close()


def execute_command(command, output=True, prefix='', grep=None):
    p = ExecuteCommand(command)
    rc = p.wait()
    result = p.result(output, prefix, grep)

    return (rc, result)

def execute_git(command, output=True, prefix='', grep=None):
    return execute_command(['git']+command, output, prefix, grep)

def get_branches(remote=False, all=False):
    git_command = ['branch', '--no-color']
    if remote:
        git_command.append('-r')
    if all:
        git_command.append('-a')
    rc, result = execute_git(git_command, output=False)
    assert rc == 0
    assert result

    def _filter_branch(branch):
        if '*' in branch:
            # Current branch:
            return branch.replace('*', '').strip()
        elif '->' in branch:
            # Branch is an alias
            return branch.split('->')[0].strip()
        return branch.strip()

    lines = result.strip().split('\n')
    return map(_filter_branch, lines)

def delete_branch(branch, force=False):
    if '/' in branch:
        if branch.startswith('remotes/'):
            branch = branch.replace('remotes/', '')
        parts = branch.split('/')
        if len(parts) == 2:
            origin_name, branch_name = parts
            execute_git(['push', origin_name, ':%s' % branch_name])
        else:
            print 'Don\'t know how to delete %s' % branch
    else:
        execute_git(['branch', '-D' if force else '-d', branch])

def get_config_properties():
    rc, output = execute_git(['config', '-l'], output=False)

    if rc != 0:
        print 'Error retrieving git config properties'
        mod_sys.exit(1)

    result = {}
	
    lines = output.split('\n')
    for line in lines:
        if '=' in line:
            pos = line.find('=')
            key = line[0 : pos].strip().lower()
            value = line[pos + 1 :].strip()
            result[key] = value
	
    return result

def is_changed():
    """ Checks if current project has any noncommited changes. """
    rc, changed_lines = execute_git(['status', '--porcelain'], output=False)
    merge_not_finished = mod_path.exists('.git/MERGE_HEAD')
    return changed_lines or merge_not_finished

