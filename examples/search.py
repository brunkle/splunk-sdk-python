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

"""A command line utility for executing Splunk searches."""

from pprint import pprint

import sys
from time import sleep

import splunk
import splunk.client as client

from utils import cmdopts

FLAGS_TOOL = [ "verbose" ]

FLAGS_CREATE = [
    "earliest_time", "latest_time", "now", "time_format",
    "exec_mode", "search_mode", "rt_blocking", "rt_queue_size",
    "rt_maxblocksecs", "rt_indexfilter", "id", "status_buckets",
    "max_count", "max_time", "timeout", "auto_finalize_ec", "enable_lookups",
    "reload_macros", "reduce_freq", "spawn_process", "required_field_list",
    "rf", "auto_cancel", "auto_pause",
]

FLAGS_RESULTS = [
    "offset", "count", "search", "field_list", "f", "output_mode"
]

FLAGS_SPLUNK = [
    "scheme", "host", "port", "username", "password", "namespace"
]

# value : dict
def slice(value, keys):
    """Returns a 'slice' of the given dict value containing only the given
       keys."""
    return dict([(k, v) for k, v in value.iteritems() if k in keys])

def cmdline(argv, flags, **kwargs):
    """A cmdopts wrapper that takes a list of flags and builds the
       corresponding cmdopts rules to match those flags."""
    rules = dict([(flag, {'flags': ["--%s" % flag]}) for flag in flags])
    return cmdopts.parse(argv, rules, ".splunkrc", **kwargs)

def main(argv):
    usage = 'usage: %prog [options] "search"'

    flags = []
    flags.extend(FLAGS_TOOL)
    flags.extend(FLAGS_CREATE)
    flags.extend(FLAGS_RESULTS)
    opts = cmdline(argv, flags, usage=usage)

    if len(opts.args) != 1:
        cmdopts.error("Search expression required", 2)
    search = opts.args[0]

    verbose = opts.kwargs.get("verbose", 1)

    kwargs_splunk = slice(opts.kwargs, FLAGS_SPLUNK)
    kwargs_create = slice(opts.kwargs, FLAGS_CREATE)
    kwargs_results = slice(opts.kwargs, FLAGS_RESULTS)

    service = client.connect(**kwargs_splunk)

    # UNDONE: Call the parser here to syntax check the query

    job = service.jobs.create(search, **kwargs_create)
    while True:
        stats = job.read(
            'isDone', 
            'doneProgress', 
            'scanCount', 
            'eventCount', 
            'resultCount')
        progress = float(stats['doneProgress'])*100
        scanned = int(stats['scanCount'])
        matched = int(stats['eventCount'])
        results = int(stats['resultCount'])
        if verbose > 0:
            status = ("\r%03.1f%% | %d scanned | %d matched | %d results" % (
                progress, scanned, matched, results))
            sys.stdout.write(status)
            sys.stdout.flush()
        if stats['isDone'] == '1': 
            if verbose > 0: sys.stdout.write('\n')
            break
        sleep(2)

    if not kwargs_results.has_key('count'): kwargs_results['count'] = 0
    results = job.results(**kwargs_results)
    while True:
        content = results.read(1024)
        if len(content) == 0: break
        sys.stdout.write(content)
        sys.stdout.flush()
    sys.stdout.write('\n')

    job.cancel()

if __name__ == "__main__":
    main(sys.argv[1:])
