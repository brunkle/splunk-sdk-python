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

"""A simple command line interface for the Splunk REST APIs."""

# UNDONE: Support for POST

import sys
from xml.etree import ElementTree

import splunk

from utils import cmdopts

# Invoke the url using the given opts parameters
def invoke(path, **kwargs):
    message = { "method": kwargs.get("method", "GET"), }
    return splunk.binding.connect(**kwargs).request(path, message)

def print_response(response):
    if response.status != 200:
        print "%d %s" % (response.status, response.reason)
        return
    body = response.body.read()
    try:
        root = ElementTree.XML(body)
        print ElementTree.tostring(root)
    except Exception:
        print body

def main():
    opts = cmdopts.parse(sys.argv[1:], {}, ".splunkrc")
    for arg in opts.args: 
        print_response(invoke(arg, **opts.kwargs))

if __name__ == "__main__":
    main()

