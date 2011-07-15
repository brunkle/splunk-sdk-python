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

"""A command line that will list out Splunk confs, or if given a conf name
   will list the contents of the given conf."""

# UNDONE: Add support for a conf 'path' to list out contents of individual
# stanza, or key value.
# UNDONE: Support for adding and deleting stanzas
# UNDONE: Extra credit points for support for modifying key/value pairs

import sys

from splunk.client import connect
from utils import error, parse

class Program:
    """Break up operations into specific methods."""
    def __init__(self, service):
        self.service = service

    def create(self, opts):
        """Create a conf stanza."""

        argv = opts.args
        count = len(argv)

        # unflagged arguments are conf, stanza, key. In this order
        # but all are optional.
        cpres = True if count > 0 else False
        spres = True if count > 1 else False
        kpres = True if count > 2 else False 

        if kpres:
            kvpair = argv[2].split("=")
            if len(kvpair) != 2:
                error("Creating a k/v pair requires key and value", 2)

        if not cpres and not spres:
            error("Conf name and stanza name is required for create", 2)

        name = argv[0]
        stan = argv[1]
        conf = self.service.confs[name]

        if not kpres:
            # create stanza
            conf.create(stan)
            return 

        # create key/value pair under existing stanza
        stanza = conf[stan]
        stanza.submit(argv[2])


    def delete(self, opts):
        """Delete a conf stanza."""

        argv = opts.args
        count = len(argv)

        # unflagged arguments are conf, stanza, key. In this order
        # but all are optional.
        cpres = True if count > 0 else False
        spres = True if count > 1 else False
        kpres = True if count > 2 else False 
        
        if not cpres:
            error("Conf name is required for delete", 2)

        if not cpres and not spres:
            error("Conf name and stanza name is required for delete", 2)

        if kpres:
            error("Cannot delete individual keys from a stanza", 2)

        name = argv[0]
        stan = argv[1]
        conf = self.service.confs[name]
        conf.delete(stan)
        
    def list(self, opts):
        """List all confs or if a conf is given, all the stanzas in it."""

        argv = opts.args
        count = len(argv)

        # unflagged arguments are conf, stanza, key. In this order
        # but all are optional
        cpres = True if count > 0 else False
        spres = True if count > 1 else False
        kpres = True if count > 2 else False 
        
        if not cpres:
            # List out the available confs
            for conf in self.service.confs: 
                print conf.name
        else:
            # Print out detail on the requested conf
            # check for optional stanza, or key requested (or all)
            name = argv[0]
            conf = self.service.confs[name]
            
            for stanza in conf:
                if (spres and argv[1] == stanza.name) or not spres:
                    print "[%s]" % stanza.name
                    entity = stanza.read()
                    for key, value in entity.iteritems():
                        if (kpres and argv[2] == key) or not kpres:
                            print "%s = %s" % (key, value)
                print

    def run(self, command, opts):
        """Dispatch the given command & args."""
        handlers = { 
            'create': self.create,
            'delete': self.delete,
            'list': self.list
        }
        handler = handlers.get(command, None)
        if handler is None:
            error("Unrecognized command: %s" % command, 2)
        handler(opts)

def main():
    """Main program."""

    usage = "usage: %prog [options] <command> [<args>]"

    argv = sys.argv[1:]

    command = None
    commands = ['create', 'delete', 'list']

    # parse args, connect and setup 
    opts = parse(argv, {}, ".splunkrc", usage=usage)
    service = connect(**opts.kwargs)
    program = Program(service)

    if len(opts.args) == 0:
        # no args means list
        command = "list"
    elif opts.args[0] in commands:
        # args and the first in our list of commands, extract 
        # command and remove from regular args
        command = opts.args[0]
        opts.args.remove(command)
    else:
        # first one not in our list, default to list
        command = "list"

    program.run(command, opts)

if __name__ == "__main__":
    main()

