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

"""An example that prints Splunk service info & settings."""

import sys

import splunk

from utils import parse

if __name__ == "__main__":
    opts = parse(sys.argv[1:], {}, ".splunkrc")
    service = splunk.client.connect(**opts.kwargs)

    info = service.info
    for key in sorted(info.keys()):
        value = info[key]
        if isinstance(value, list):
            print "%s:" % key
            for item in value: print "    %s" % item
        else:
            print "%s: %s" % (key, value)

    settings = service.settings.read()
    print "Settings:"
    for key in sorted(settings.keys()):
        value = settings[key]
        print "    %s: %s" % (key, value)
