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

import server
import webbrowser
import sys
import os

import utils
import urllib

PORT = 8080

def main(argv):
    usage = "usage: %prog [options]"

    redirect_port_args = {
        "redirectport": {
            "flags": ["--redirectport"],
            "default": PORT,
            "help": "Port to use for redirect server (default: %s)" % PORT,
        },
    }

    opts = utils.parse(argv, redirect_port_args, ".splunkrc", usage=usage)

    # We have to provide a sensible value for namespace
    namespace = opts.kwargs["namespace"]
    namespace = namespace if namespace else "-"

    # Encode these arguments
    args = urllib.urlencode([
            ("scheme", opts.kwargs["scheme"]),
            ("host", opts.kwargs["host"]),
            ("port", opts.kwargs["port"]),
            ("redirecthost", "localhost"),
            ("redirectport", opts.kwargs["redirectport"]),
            ("username", opts.kwargs["username"]),
            ("password", opts.kwargs["password"]),
            ("namespace", namespace)
        ]),

    # Launch the browser
    webbrowser.open("file://%s" % os.path.join(os.getcwd(), "explorer.html?%s" % args))

    # And server the files
    server.serve(opts.kwargs["redirectport"])
        
if __name__ == "__main__":
    main(sys.argv[1:])