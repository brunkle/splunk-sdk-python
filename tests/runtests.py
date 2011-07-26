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
#
# Run all the Splunk Python SDK tests

import os

# Set up the environment for coverage, even though it might not get used
os.environ["COVERAGE_PROCESS_START"] = "../tests/.coveragerc"

files = [
    "test_data.py",
    "test_binding.py",
    "test_proxy.py",
    "test_client.py",
    "test_examples.py",
]

for file in files: 
    command = "python %s" % file
    print "Running Test: %s" % file
    os.system(command)
