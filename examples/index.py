#!/usr/bin/env python
#
# Copyright 2011 Splunk, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"): you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""A command line utility for interacting with Splunk indexes."""

# UNDONE: Improve command line help to show the following commands:
#
#     clean [<index>]+
#     create <index> [options]
#     disable [<index>]+
#     enable [<index>]+
#     list [<index>]*
#     reload [<index>]+
#     update <index> [options]
#
# UNDONE: Implement a delete command: clean, remove stanzas from indexes.conf,
#  restart server, delete db files.

import sys

from splunk.client import connect

from utils.cmdopts import cmdline, error, parse

class Program:
    def __init__(self, service):
        self.service = service

    def clean(self, argv):
        self.foreach(argv, lambda index: index.clean())

    def create(self, argv):
        """Create an index according to the given argument vector."""

        if len(argv) == 0: 
            error("Command requires an index name", 2)

        name = argv[0]

        if self.service.indexes.contains(name):
            print "Index '%s' already exists" % name
            return

        # Read item metadata and construct command line parser rules that 
        # correspond to each editable field.

        # Request editable fields
        itemmeta = self.service.indexes.itemmeta()
        fields = itemmeta['eai:attributes'].optionalFields

        # Build parser rules
        rules = dict([(field, {'flags': ["--%s" % field]}) for field in fields])

        # Parse the argument vector
        opts = cmdline(argv, rules)

        # Execute the edit request
        self.service.indexes.create(name, **opts.kwargs)

    def disable(self, argv):
        self.foreach(argv, lambda index: index.disable())

    def enable(self, argv):
        self.foreach(argv, lambda index: index.enable())

    def list(self, argv):
        """List available indexes if no names provided, otherwise list the
           properties of the named indexes."""

        def read(index):
            print index.name
            for key, value in index.read().iteritems(): 
                print "    %s: %s" % (key, value)

        if len(argv) == 0:
            for index in self.service.indexes:
                count = index['totalEventCount']
                print "%s (%s)" % (index.name, count)
        else:
            self.foreach(argv, read)

    def run(self, command, argv):
        # Dispatch the command
        commands = { 
            'clean': self.clean,
            'create': self.create,
            'disable': self.disable,
            'enable': self.enable,
            'list': self.list,
            'reload': self.reload,
            'update': self.update,
        }
        if command not in commands.keys():
            error("Unrecognized command: %s" % command, 2)
        commands[command](argv)

    def reload(self, argv):
        self.foreach(argv, lambda index: index.reload())

    def foreach(self, argv, func):
        """Apply the function to each index named in the argument vector."""
        opts = cmdline(argv)
        if len(opts.args) == 0:
            error("Command requires an index name", 2)
        for name in opts.args:
            if not self.service.indexes.contains(name):
                error("Index '%s' does not exist" % name, 2)
            index = self.service.indexes[name]
            func(index)

    def update(self, argv):
        """Update an index according to the given argument vector."""

        if len(argv) == 0: 
            error("Command requires an index name", 2)
        name = argv[0]
        if not self.service.indexes.contains(name):
            error("Index '%s' does not exist" % name, 2)
        index = self.service.indexes[name]

        # Read entity metadata and construct command line parser rules that 
        # correspond to each editable field.

        # Request editable fields
        fields = index.readmeta()['eai:attributes'].optionalFields

        # Build parser rules
        rules = dict([(field, {'flags': ["--%s" % field]}) for field in fields])

        # Parse the argument vector
        opts = cmdline(argv, rules)

        # Execute the edit request
        index.update(**opts.kwargs)

def main():
    usage = "usage: %prog [options] <command> [<args>]"

    # Split the command line into 3 parts, the apps arguments, the command
    # and the arguments to the command. The app arguments are used to
    # establish the binding context and the command arguments are command
    # specific.

    argv = sys.argv[1:]

    # Find the index of the command argument (the first non-kwarg)
    cmdix = -1
    for i in xrange(len(argv)):
        if not argv[i].startswith('-'):
            cmdix = i
            break

    if cmdix == -1: # No command
        appargv = argv
        command = "list"
        cmdargv = []
    else:
        appargv = argv[:cmdix]
        command = argv[cmdix]
        cmdargv = argv[cmdix+1:]

    opts = parse(appargv, {}, ".splunkrc", usage=usage)
    service = connect(**opts.kwargs)
    program = Program(service)
    program.run(command, cmdargv)

if __name__ == "__main__":
    main()

